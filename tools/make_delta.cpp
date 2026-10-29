// Developer-only bounded copy/literal encoder. No engine or game code.
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <unordered_map>
#include <vector>
using Bytes=std::vector<unsigned char>;
Bytes read(const char* path){std::ifstream f(path,std::ios::binary|std::ios::ate);if(!f)throw std::runtime_error("input");auto n=f.tellg();f.seekg(0);Bytes b(static_cast<size_t>(n));f.read(reinterpret_cast<char*>(b.data()),n);if(!f)throw std::runtime_error("read");return b;}
void put(Bytes& out,uint64_t n,unsigned size){for(unsigned i=0;i<size;i++)out.push_back(static_cast<unsigned char>(n>>(i*8)));}
uint64_t key(const unsigned char* p){uint64_t k;std::memcpy(&k,p,8);return k;}
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("usage: make_delta BASE TARGET OUTPUT");
 auto base=read(argv[1]),target=read(argv[2]);
 std::unordered_map<uint64_t,uint32_t> index;index.reserve(base.size()/64);
 for(size_t i=0;i+64<=base.size();i+=64)index.emplace(key(base.data()+i),static_cast<uint32_t>(i));
 Bytes out={'W','W','B','F','D','E','L','1'};put(out,target.size(),8);put(out,0,4);uint32_t count=0;
 size_t pos=0,start=0;
 auto literal=[&](){if(pos>start){out.push_back(1);put(out,pos-start,4);out.insert(out.end(),target.begin()+start,target.begin()+pos);++count;}start=pos;};
 while(pos+64<=target.size()){
  auto found=index.find(key(target.data()+pos));
  if(found==index.end()||std::memcmp(base.data()+found->second,target.data()+pos,64)){++pos;continue;}
  size_t source=found->second,n=64,limit=std::min(base.size()-source,target.size()-pos);
  while(n+64<=limit&&!std::memcmp(base.data()+source+n,target.data()+pos+n,64))n+=64;
  while(n<limit&&base[source+n]==target[pos+n])++n;
  literal();out.push_back(0);put(out,source,8);put(out,n,4);++count;pos+=n;start=pos;
 }
 pos=target.size();literal();for(unsigned i=0;i<4;i++)out[16+i]=static_cast<unsigned char>(count>>(8*i));
 std::ofstream f(argv[3],std::ios::binary);f.write(reinterpret_cast<char*>(out.data()),out.size());if(!f)throw std::runtime_error("write");
 std::cout<<"operations="<<count<<" raw_delta_bytes="<<out.size()<<"\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;} }
