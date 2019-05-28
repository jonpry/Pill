#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#include <vector>
#include <map>

using namespace std;

//TODO: there are 2 versions of the header with some kind of offset difference. 
//This code only handles one version of it

#define PAGE(x) (x & ~0xFFFul)
#define OFS(x)  (x & 0xFFFul)

enum {LIST_TYPE=2,FIX_TYPE,SYM_TYPE=5,FLO_TYPE=8,STR_TYPE};

map<uint64_t,uint64_t> pgmap;
map<uint64_t,uint16_t> typmap;
uint64_t orig_strtab, strtab;
uint8_t *buf;

const char *codeNames[] = {"Inline Literal", "FuncCall", "KCompile", "SCompile",  
                           "GetProp", "PutProp", "Pop", "Push", 
                           "DefGlobalFun", "DefSGlobalVar", "DefSLocalVar", "SetSLocalVar", 
                           "SetSLexVar", "SetSGlobalVar", "SetKLocalVar", "SetKGlobalVar", 
                           
                           "ForBegin", "ForCheck", "ForeachBegin", "ForeachCheck", //ForBegin = 16
                           "Forallbegin", "ForallCheck", "ExistsBegin", "ExistsCheck", 
                           "SetofBegin", "SetofCheck", "TailReturn", "DebugBreak", 
                           "NativeCall", "VerifyFun", "KDefaultsEnd", "SDefaultsEnd", 

                           "CodeBegin", "CodeEnd", "FuncEnd", "FuncReturn", //Codebegin = 32
                           "FormEnd", "EndReturn", "AssignOp", "EndDebug",
                           "DebugFormEnd", "ProgBegin", "ProgEnd", "TailProgEnd", 
                           "KLetEnd", "ProgLabel", "litblock", "BranchIfNotZeroAndLoadZero", 

                           "BranchIfZero", "BranchIfNotZero", "BranchForward", "BranchBackward", //BEZ = 48
                           "BranchIfBound", "BranchIfZeroLoad1", "BNEQ", "BNEQ2", 
                           "BNEQI", "BNEQI2", "Branch NOT IN", "Branch NOT IN2", 
                           "ProgGo", "Break", "CondImply", "DebugExit", 

                           "LoadNil", "LoadT", "LoadLiteral", "InlineInt", 
                           "RefKLocalVar", "RefKGlobalVar", "RefKLocalFunc", "RefSLocalVar", 
                           "RefSLexVar", "RefSGlobalVar", "RefSGlobalFunc", "LRefGlobalVar", 
                           "LRefLexVar", "LoadFunction", "MakeClosure", "Reserved",
 
                           "Call", "TailCall", "NCall", "TailNCall", 
                           "ICall", "TailICall", "Environment", "KLetBegin", 
                           "ArgsOriginal", "ArgsUnbound", "PCall", "TailPCall", 
                           "DebugEnter", "DebugBegin", "DebugAtomic", "TCovHitCount", 

                           "" };

uint8_t codeTypes[] = {0x11, 0xf, 0x13, 0x13, 
                      0x20, 0x9, 0x11, 0x11, 
                      0x20, 0x20, 0x21, 0x21, 
                      0x21, 0x20, 0x20, 0x20, 

                      0x22, 0x22, 0x22, 0x22, 
                      0x22, 0x22, 0x22, 0x22, 
                      0x22, 0x22, 0x11, 0x19, 
                      0x1b, 0x22, 0x16, 0x16, 

                      0x14, 0x15, 0x15, 0x11, 
                      0x12, 0x12, 0x7, 0x12,
                      0x18, 0x23, 0xb, 0xb, 
                      0xb, 0x22, 0x23, 0x22, 

                      0x22, 0x22, 0x22, 0x22, 
                      0x22, 0x22, 0x22, 0x22, 
                      0x22, 0x22, 0x22, 0x22, 
                      0x1, 0x6, 0x11, 0x15, 
 
                      0x1a, 0x1a, 0x3, 0x6, 
                      0x1d, 0x1d, 0x1d, 0x1e, 
                      0x1e, 0x1d, 0x1d, 0x1d, 
                      0x1e, 0x1f, 0x1f, 0x11, 

                      0xf, 0xf, 0xa, 0xa, 
                      0xf, 0xf, 0x6, 0xd, 
                      0x0, 0x0, 0x10, 0x10, 
                      0x11, 0x17, 0x11, 0x1c, 

                      0x1a, 0x1a, 0x3, 0x6, 
                      0x1d, 0x1d, 0x1d, 0x1e, 
                      0x1e, 0x1d, 0x1d, 0x1d, 
                      0x1e, 0x1f, 0x1f, 0x11, 

                      0xf, 0xf, 0xa, 0xa, 
                      0xf, 0xf, 0x6, 0xd, 
                      0x0, 0x0, 0x10, 0x10, 
                      0x11, 0x17, 0x11, 0x1c};

const char* atoms[]= {"dummy", "dummy" , "dummy" , "call" , 
                     "call" , "call" , "call" , "call" , 
                     "call" , "dummy" , "if" , "then" , 
                     "else" , "while" , "when" , "unless" , 

                     "case" , "caseq" , "decode" , "cond" , 
                     "and" , "or" , "for" , "foreach" , 
                     "forall" , "setof" , "exists" , "prog1" , 
                     "prog2" , "progn" , "prog" , "go" , 

                     "setq" , "quote" , "defun" , "defvar" , 
                     "def" , "lambda" , "nlambda" , "macro" , 
                     "procedure" , "nprocedure" , "mprocedure" , "eval" , 
                     "getq" , "getqq" , "putpropq" , "putpropqq" , 

                     "predecrement" , "preincrement" , "postdecrement" , "postincrement" , 
                     "setqbitfield1" , "setqbitfield" , "declare" , "dummy" , 
                     "dummy" , "dummy" , "defprop" , "getsgq" , 
                     "setsgq" , "sstatus" , "pp" , "fscanf" , 

                     "scanf" , "sprintf" , "toplevelset" , "errset" , 
                     "dummy" , "dummy" , "define" , "body" , 
                     "local" , "recargs" , "seqargs" , "begin" , 
                     "letseq" , "letrec" , "let" , "dummy" , 

                     "do" , "dummy" , "dummy" , "imply" , 
                     "theenvironment" , "break" , "export" , "named" , 
                     "dummy" , "dummy" , "dummy" , "kcompile" , 
                     "sfor" , "sforeach" , "sforall" , "ssetof" , 

                     "sexists" , "scompile" , "compilein"};


void print_obj(uint64_t old_adr){
   old_adr &= ~0x7ul;
   //printf("Obj @ 0x%lx %d\n", old_adr, typmap[PAGE(old_adr)]);
   if(!old_adr){
      printf("Nil");
      return;
   }
   uint8_t *obj = (uint8_t*)(pgmap[PAGE(old_adr)] + OFS(old_adr));
   assert(pgmap.find(PAGE(old_adr)) != pgmap.end());

   switch(typmap[PAGE(old_adr)]){
      case LIST_TYPE: {
//         printf("List\n");
//         printf("Lis1 0x%lx\n", *(uint64_t*)&obj[8]);
//         printf("Lis2 0x%lx\n", *(uint64_t*)&obj[0x10]);

         printf("(");
         print_obj(*(uint64_t*)&obj[8]);
         printf(",");
         print_obj(*(uint64_t*)&obj[0x10]);
         printf(")");
         } break;
      case FLO_TYPE: {
         printf("%f", *(double*)&obj[8]);
         } break;
      case STR_TYPE: {
         printf("\"%s\"", &buf[*(uint64_t*)&obj[8] - orig_strtab + strtab]);
         } break;
      case SYM_TYPE: {
         printf("Sym:\"%s\"", &buf[*(uint64_t*)&obj[8] - orig_strtab + strtab]);
         } break;
      default:
         printf("Type: %d\n", typmap[PAGE(old_adr)]);
         assert(false);
   }
}

void printins(uint64_t ofst){
        uint64_t op=*(uint64_t*)&buf[ofst];
        uint8_t code = op & 0xFF;
        uint64_t u48 = op >> 16;
        uint32_t u32 = u48;
        uint64_t u56 = op >> 8;
        if(pgmap.find(PAGE(op)) != pgmap.end()){
              printf("Literal: 0x%lx, ", op);
              print_obj(op);
              printf("\n");
              return;
        }

        if(code & 1 == 0){
           printf("Load literal\n");
           if(pgmap.find(PAGE(op)) != pgmap.end()){
              print_obj(op);
              printf("\n");
           }else{
              assert(false);
           }
           return;
        }
        if(code & 0xc0 == 0xc0){
              printf("Push + ");
           }
           if (code & 0x80 == 0) {
             code &= 0x7f;
           } else {
             code &= 0xbf;
        }
        printf("%s\n", codeNames[code>>1]);

        uint8_t type = codeTypes[code>>1];
  
        if (type == 0x1c) {
          printf("%d\n",u32);
        }else if(type == 0x10){
          printf("PCall 0x%lX 0x%X %s\n", u56&0xff, u32, atoms[(u56&0xff)>>1]);
        }else if(type == 9 || type == 0x12 || type == 7 || type == 0x20 || type == 8 || type == 0x21 || type == 0x11 || type == 0x22){
          uint8_t atom = u56;
          printf("Atom %d %s\n", atom, atoms[atom]);
        }else if(type == 0x1d){
            //printf("0x%X 0x%lX 0x%X 0x%lX\n",type,u56&0xFF, code, u48); 
            printins(ofst+u32*8);
        }else if(type == 0x1a){
            //Load true
        }else if(type == 0xf){
            //Lots of different types of calls
        }else{ 
            printf("Ukn: 0x%X 0x%lX 0x%X 0x%lX\n",type,u56&0xFF, code, u48); 
        }
}

int main(){
   vector<uint64_t> strings, syms, lists;

   //Load entire file into memory
   FILE* f = fopen("jon.ctx","r");
   fseek(f,0,SEEK_END);
   size_t sz = ftell(f);
   fseek(f,0,SEEK_SET);
   buf = (uint8_t*)valloc(sz);
   fread(buf,sz,1,f);
   fclose(f);

   uint64_t ofst=0;
   //Extract fields from header
   uint64_t ulong = *(uint64_t*)&buf[0x10];
   uint32_t uint = *(uint32_t*)&buf[0x18];

   printf("Long 0x%lX int 0x%X\n", ulong, uint);

   uint32_t version = *(uint32_t*)&buf[0x20];
   printf("Version 0x%X\n", version);

   uint32_t hdr_size = *(uint32_t*)&buf[0x30];

   uint32_t nns = *(uint32_t*)&buf[0x48];
   uint32_t narrays = *(uint32_t*)&buf[0x60];
   uint32_t nstrings = *(uint32_t*)&buf[0x70];
   orig_strtab = *(uint64_t*)&buf[0x78];
   uint64_t orig_arytab = *(uint64_t*)&buf[0x40];

   uint32_t nuts = *(uint32_t*)&buf[0x88];
   uint32_t nblocks = *(uint32_t*)&buf[0x90];

   printf("Number of blocks: 0x%X, hdr_size: 0x%X, arrays: 0x%X, uts: 0x%X, strings: 0x%X, nss: 0x%X\n", nblocks, hdr_size, narrays, nuts, nstrings, nns);
   printf("%lx %lx\n", orig_arytab, orig_strtab);

   printf("lname 0x%lX\n", 0x12717-0xffc8+orig_strtab);

   ofst+=hdr_size;
   //exit(0);
   for(uint32_t i = 0; i < nblocks; i++){

       uint8_t *ukn8 = (uint8_t*)&buf[ofst];
       uint16_t *ukn16 = (uint16_t*)&buf[ofst];
       uint64_t *ukn64 = (uint64_t*)&buf[ofst];
       //ukn1 = __bswap_64(ukn1);
       uint16_t cell_size = ukn16[0];
       uint16_t block_size = ukn16[2];
       uint16_t cell_type = ukn16[1];
       uint64_t orig_addr = *(uint64_t*)&buf[0x98+i*8];

       assert(block_size <= 4096);
 

       //Blocks are limited to 4k in size and get mapped to a new page
       uint8_t* new_block = (uint8_t*)valloc(4096);
       memcpy(new_block,&buf[ofst],4096);
       pgmap[PAGE(orig_addr)] = (uint64_t)new_block;
       typmap[PAGE(orig_addr)] = cell_type;
       printf("Orig 0x%lx\n", orig_addr);
       ofst += 0x20;

       //printf("Ukn1 0x%llX\n", *(uint64_t*)ukn8);
       assert(block_size % cell_size == 0);
       uint16_t cnt = block_size / cell_size;
       for(uint32_t j=0; j < cnt; j++){
//           printf("At 0x%lX type: %x\n", ofst, cell_type);
#if 1
           if(cell_type == 0x1) { //Function
        printf("block %3u orig 0x%lX Cell Size %3d Type %d Size %6d Flags %6x\n", i, *(uint64_t*)&buf[0x98+i*8]
                          ,cell_size,cell_type,block_size,ukn16[3]);
                          //CONCAT44(uVar45,(uint)puVar31[3]),puVar31 + 6);
        printf("block 0x%lX, 0x%lX, 0x%lX\n", ukn64[1],ukn64[2],ukn64[3]); ////Name of context
              printf("Fun1 0x%X 0x%X\n", *(uint32_t*)&buf[ofst+0], *(uint32_t*)&buf[ofst+4]); 
              printf("Fun2 0x%lx\n", *(uint64_t*)&buf[ofst+8]);
              printf("Fun3 0x%lx\n", *(uint64_t*)&buf[ofst+0x10]);
              printf("Fun4 0x%lx\n", *(uint64_t*)&buf[ofst+0x18]);
           }
#endif
           if(cell_type == 0x2) { //List
        printf("block %3u orig 0x%lX current 0x%lX Cell Size %3d Type %d Size %6d Flags %6x\n", i, orig_addr, &buf[ofst]
                          ,cell_size,cell_type,block_size,ukn16[3]);
                          //CONCAT44(uVar45,(uint)puVar31[3]),puVar31 + 6);
        printf("block 0x%lX, 0x%lX, 0x%lX\n", ukn64[1],ukn64[2],ukn64[3]); ////Name of context

              printf("Lis0 0x%x\n", *(uint8_t*)&buf[ofst+4]);
              printf("Lis1 0x%lx\n", *(uint64_t*)&buf[ofst]);
              printf("Lis1 0x%lx\n", *(uint64_t*)&buf[ofst+8]);
              printf("Lis2 0x%lx\n", *(uint64_t*)&buf[ofst+0x10]);
              printf("List @ 0x%lx\n",( (uint64_t)(orig_addr + 0x20 + j * cell_size)));

              lists.push_back( (uint64_t)(orig_addr + 0x20 + j * cell_size));

           }

           if(cell_type == 0x9) { //String
              printf("Str1 0x%lX\n", *(uint64_t*)&buf[ofst]);
              printf("Str2 %lX\n", *(uint64_t*)&buf[ofst+8]);
              strings.push_back( *(uint64_t*)&buf[ofst+8]);
           }

#if 0

           if(cell_type == 0x3) { //Fixnum

           }
           if(cell_type == 0x5) { //Symbol
              printf("Sym1 0x%lX\n", *(uint64_t*)&buf[ofst]);
              printf("Sym2 %lX\n", *(uint64_t*)&buf[ofst+8]);
              printf("Sym3 %lX\n", *(uint64_t*)&buf[ofst+16]);
              printf("Sym4 %lX\n", *(uint64_t*)&buf[ofst+24]);
              printf("Sym5 %lX\n", *(uint64_t*)&buf[ofst+32]);
              printf("Sym6 %lX\n", *(uint64_t*)&buf[ofst+40]);
              printf("Sym7 %lX\n", *(uint64_t*)&buf[ofst+48]);

              uint64_t sym4 = *(uint64_t*)&buf[ofst+40];

              sym4 = ((sym4 >> 0x11) * 8) + ((sym4 >> 0xc & 0x1f) * 8);
              uint32_t ofs = *(uint32_t*)&buf[ofst+0x28];
              printf("Sym44 %lX\n", sym4);
              printf("Sym45 %X\n", ofs);

              syms.push_back( *(uint64_t*)&buf[ofst+8]);
           }
           if(cell_type == 0x8) { //FloNum
              printf("Flo1 0x%llX\n", *(uint64_t*)&buf[ofst]);
              printf("Flo2 %le\n", *(double*)&buf[ofst+8]);
           }
#endif
           ofst += cell_size;
       }
 
   }
   strtab = ofst;
   ofst += nstrings;
 
   uint64_t arytab = ofst;
#if 1
   for(uint32_t i=0; i < narrays/8; i++){
      printins(ofst);
      ofst+=8;
   }
#endif

   printf("S : %s\n", &buf[strtab+0x2a]); 


   printf("Strings : 0x%lx\n", strings.size()); 
   printf("Arrays at 0x%lx\n", arytab);
exit(0);
   for(auto it=lists.begin(); it!=lists.end(); it++){
      print_obj(*it);
      printf("\n");
   }



   exit(0);

   for(auto it=strings.begin(); it!=strings.end(); it++){
      printf("%s\n", &buf[*it - orig_strtab + strtab]);
   }
   for(auto it=syms.begin(); it!=syms.end(); it++){
      printf("%s\n", &buf[*it - orig_strtab + strtab]);
   }

}
