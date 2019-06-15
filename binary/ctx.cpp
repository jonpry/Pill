//Copyright (C) 2019 Jon Pry
//
//This file is part of Pill.
//
//Pill is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 2 of the License, or
//(at your option) any later version.
//
//Pill is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with Pill.  If not, see <http://www.gnu.org/licenses/>.

#include "main.h"

//TODO: there are 2 versions of the header with some kind of offset difference. 
//This code only handles one version of it

#define PAGE(x) (x & ~0xFFFul)
#define OFS(x)  (x & 0xFFFul)

enum {FUN_TYPE=1,LIST_TYPE,FIX_TYPE,SYM_TYPE=5,FLO_TYPE=8,STR_TYPE};

map<uint64_t,uint64_t> pgmap;
map<uint64_t,uint16_t> typmap;
uint64_t orig_strtab, strtab, arytab;
uint8_t *buf;

set<uint64_t> consumed;

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
                      0x20, 0xd, 0x21, 0x21, 
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

std::string to_hex(uint64_t to_convert){
    std::string result;
    std::stringstream ss;
    ss << std::hex <<to_convert;
    ss >> result;
    return result;
}

SList* print_obj(uint64_t old_adr){
   old_adr &= ~0x7ul;
   //printf("Obj @ 0x%lx %d\n", old_adr, typmap[PAGE(old_adr)]);
   if(!old_adr){
      printf("Nil");
      return new SList(0,"nil");
   }
   uint8_t *obj = (uint8_t*)(pgmap[PAGE(old_adr)] + OFS(old_adr));
   assert(pgmap.find(PAGE(old_adr)) != pgmap.end());

   switch(typmap[PAGE(old_adr)]){
      case FUN_TYPE: {
         return new SList(old_adr,"anon_func_" + to_hex(old_adr));
         } break;
      case LIST_TYPE: {
//         printf("List\n");
//         printf("Lis1 0x%lx\n", *(uint64_t*)&obj[8]);
//         printf("Lis2 0x%lx\n", *(uint64_t*)&obj[0x10]);

         vector<SList*> list;
         list.push_back(print_obj(*(uint64_t*)&obj[8]));
         list.push_back(print_obj(*(uint64_t*)&obj[0x10]));
         return new SList(old_adr,"static_list_" + to_string(old_adr), &list); 
         } break;
      case FLO_TYPE: {
         double d = *(double*)&obj[8];
         printf("%f", d);
         char flo[64];
         sprintf(flo,"%.16g",d);
         return new SList(old_adr,flo);
         } break;
      case STR_TYPE: {
         uint64_t ofst=*(uint64_t*)&obj[8] - orig_strtab + strtab;
         printf("\"%s\"", &buf[ofst]);
         return new SList(ofst,"\"" + string((char*)&buf[ofst]) + "\"");
         } break;
      case SYM_TYPE: {
         uint64_t ofst=*(uint64_t*)&obj[8] - orig_strtab + strtab;
         printf("Sym:\"%s\"", &buf[ofst]);
         consumed.insert(ofst);
         return new SList(ofst,(char*)&buf[ofst]);
         } break;
      default:
         printf("Ukn Type: %d\n", typmap[PAGE(old_adr)]);
         return new SList(old_adr,"ukn_literal");
   }
   return 0;
}

#define MOV_TO_STACK(dst) do { \
        assert(!stack.empty()); \
        dst.push_back(stack.back()); \
        stack.pop_back(); \
   }\
   while(false)

SList* printins(uint64_t *pofst, vector<SList*> &stack,bool force_sym=false){
    uint64_t ofst = *pofst;
    vector<SList*> tstack;
    uint64_t op=*(uint64_t*)&buf[ofst];
    uint8_t code = op & 0xFF;
    uint64_t u48 = op >> 16;
    uint32_t u32 = u48;
    uint64_t u56 = op >> 8;
    uint8_t u8 = u56;
    bool do_push=false;


    printf("Op: 0x%lX Code: 0x%X %d @0x%lX\n", op, code, !(code & 1), (ofst-arytab)/8);
#if 0
    if(pgmap.find(PAGE(op)) != pgmap.end()){
          printf("Literal: 0x%lx, @0x%lx ", op, (ofst-arytab)/8);
          SList *ret =print_obj(op);
          printf("\n");
          stack.push_back(ret);
          return ret;
    }
#endif
    if(!(code & 1) || force_sym){
       printf("Load literal\n");
       if(pgmap.find(PAGE(op)) != pgmap.end()){
          printf("Literal: 0x%lx, @0x%lx ", op, (ofst-arytab)/8);
          SList *ret =print_obj(op);
          printf("\n");
          stack.push_back(ret);
          return ret;
        }else{
  //        assert(false);
       }
   //    stack.push_back(0);
       return 0;
    }
    uint8_t raw_code = code;
    if(code & 0xc0 == 0xc0){
          printf("Push + ");
          do_push=true;
       }
       if (code & 0x80 == 0) {
         code &= 0x7f;
       } else {
         code &= 0xbf;
    }
    if(!do_push)
       printf("No Push\n");
    printf("%s\n", codeNames[code>>1]);

    uint8_t type = codeTypes[code>>1];

    if (type == 0x1c) {
      printf("%d\n",u32);
      return new SList(ofst,"int_1c");
    }else if(type == 0x10){
      printf("PCall 0x%X 0x%X 0x%X\n", code, u8, u32); //Comparison predicates
    
      vector<SList*> args;
      for(int i=0; i < u32; i++){
          args.push_back(stack.back());
          stack.pop_back();
      }
      string name = "pcall_" + to_string(u8);
      if(u8 == 0x17)
          name = "equalsp";
      else if(u8 == 0x18)
          name = "nequalsp";
      else if(u8 == 0xa)
          name = "divp";
      else if(u8 == 0x9)
          name = "mulp";
      else if(u8 == 0x8)
          name = "subp";
      else if(u8 == 0x7)
          name = "addp";
      else if(u8 == 0xb)
          name = "ltp";
      else if(u8 == 0xc)
          name = "lep";
      else if(u8 == 0xd)
          name = "gtp";
      else if(u8 == 0xe)
          name = "gep";
      else if(u8 == 0x12)
          name = "cadr"; 
      else if(u8 == 0x13)
          name = "cdr"; 
      else if(u8 == 0x10 || u8 == 0x11)
          name = "arrayindex";
      else if(u8 == 0x14)
          name = "cons";
      else if(u8 == 0x19)
          name = "notp"; 
      else if(u8 == 0xf)
          name = "eval";
      else if(u8 == 0x3f)
          name = "return";
      else if(u8 == 0x1d)
          name = "listp";
      else if(u8 == 0x22)
          name = "stringp";
      else if(u8 == 0x25)
          name = "fixp";
      else if(u8 == 0x26)
          name = "floatp";

      reverse(args.begin(),args.end());
      SList* ret=new SList(ofst,name,&args);
      if(do_push) 
         stack.push_back(ret);
      return ret;
    }else if(raw_code == 0x5d){ //Some sort of list
        vector<SList*> args;
        for(int i=0; i < 4; i++){
            uint64_t lofst = ofst+(((int32_t)u32)+i)*8;
            printins(&lofst,tstack,false);
        }
        SList *ret = new SList(ofst,"case_value",&tstack);
        if(do_push)
           stack.push_back(ret);
        return ret;
    }else if(type == 0x9 || type == 0x12 || type == 7 || type == 0x20  || type == 0x11 || type == 0x22){
      uint8_t atom = u8;
      printf("Atom %d %s Type: 0x%X Code: 0x%X u32: 0x%X op: 0x%lx u8:0x%X @0x%lx\n", atom, atoms[atom], type, code, u32, op, u8, (ofst-arytab)/8);

      if(u8 == 0x20 || u8 == 0x2C || code == 0x1d) { //One arg, one literal, 1d is setq
        string extra="";
        if(code == 0x1d)
          extra = "_1d_" + to_string(u8) + "_" + to_string(u32);
        vector<SList*> args;

        uint64_t lofst = ofst+((int32_t)u32)*8;
        args.push_back(printins(&lofst,tstack,true));

        MOV_TO_STACK(args);
        SList *ret = new SList(ofst,atoms[atom] + extra,&args);
        if(do_push)
           stack.push_back(ret);
        return ret;
      }

      if(u8 == 3 || u8 == 0x15 || u8 == 0x1a || u8 == 0x41 || u8==0x14 || u8==0x17 || u8 == 0x16 || u8 == 0x8 || u8 == 0xd || u8 == 0x52 || u8 == 0x10 || u8 == 0xe) { //Just like call
        vector<SList*> args;
        if(u8 == 0x10) //Case
          u32++;
        for(uint32_t i=0; i < u32; i++){
            args.push_back(stack.back());
            if(stack.empty())
               exit(0);
            assert(!stack.empty());
            stack.pop_back();
        }
        reverse(args.begin(),args.end());
        string extra = "";
        if(string("dummy") == atoms[atom] || u8 == 0xe)
          extra = "_" + to_string(u32) + "_" + to_string(u8);

        if(u8==0xe){
           for(auto it=args.begin(); it!=args.end(); it++){
                //extra += "_" + (*it)->m_atom;
                //assert((*it)->m_atom != "end_ag");
           }
        }

        SList* ret=new SList(ofst,atoms[atom] + extra,&args);

        if(do_push)    
           stack.push_back(ret);
        return ret;
      }

      //TODO: Probably like call
      if(u8 == 0x4e){
        vector<SList*> args;
        for(uint32_t i=0; i < u32; i++){
            MOV_TO_STACK(args);
        }
        reverse(args.begin(),args.end());

        SList *ret = new SList(ofst,"let_atom_" + to_string(stack.size()) + "_" + to_string(u32), &args);

        if(do_push)    
           stack.push_back(ret);
        return ret;
      }

      if(u8 == 0x2E) { //Two args, one literal

        vector<SList*> args;
        uint64_t lofst = ofst+((int32_t)u32)*8;
        MOV_TO_STACK(args);
        args.push_back(printins(&lofst,tstack,true));
        MOV_TO_STACK(args);
        reverse(args.begin(),args.end());        
        SList *ret = new SList(ofst,atoms[atom],&args);
        if(do_push)
           stack.push_back(ret);
        return ret;
      }

      if(u8 == 0x33) { //postinc
         vector<SList*> args;
         MOV_TO_STACK(args);

         SList* ret=new SList(ofst,atoms[atom],&args);
         if(do_push)    
            stack.push_back(ret);
         return ret;
      }

      if(u8 == 0xa) { //if
        vector<SList*> args;
//        for(uint32_t i=0; i < u32; i++)
//           MOV_TO_STACK(args);
        uint32_t consumed=0;
        MOV_TO_STACK(args);
        consumed+=1;
        if(args.back()->m_atom.rfind("then",0)==0 || args.back()->m_atom.rfind("else",0)==0)
           consumed += args.back()->m_list.size();
        MOV_TO_STACK(args);
        if(consumed < u32 -1){
          consumed+=1;
          if(args.back()->m_atom.rfind("then",0)==0 || args.back()->m_atom.rfind("else",0)==0)
             consumed += args.back()->m_list.size();
          MOV_TO_STACK(args);
        }
        string fail="";
        if(consumed+1!=u32)
          fail="fail";
        if(u32==2) //Extra one for some reason
          MOV_TO_STACK(args);
        reverse(args.begin(),args.end());        
        SList *ret = new SList(ofst,"if_atom_" + fail + "_" + to_string(u32) + "_" + to_string(consumed+1) + "_" + to_string(args.size()), &args);
        if(do_push)
           stack.push_back(ret);
        return ret;
      }         

      if(u8 == 0x11) { //case
        SList *ret = new SList(ofst,"case_atom");
        //if(do_push)
        //   stack.push_back(ret);
        return ret;
      }         

      if(u8 == 3 || u8 == 0x4 || u8 == 0x5 || u8 == 0x6){
         SList *ret = new SList(ofst,"call_atom");
         return ret;
      }

      if(u8 == 0x1) { //unknown
        SList *ret = new SList(ofst,"ukn1_atom");
        //if(do_push)
        //   stack.push_back(ret);
        return ret;
      }  

      if(u8 == 0x2) { //unknown
        SList *ret = new SList(ofst,"ukn2_atom");
        //if(do_push)
        //   stack.push_back(ret);
        return ret;
      }  

#if 0
      if(u8 == 0xe) { //when
         vector<SList*> args;
         MOV_TO_STACK(args);
         SList *ret = new SList(ofst,"when_atom_" + to_string(u32));
         if(do_push)
           stack.push_back(ret);
         return ret;         
      }
#endif
      if( u8 == 0xb || u8 == 0xc) { //Then/else - One arg
        printf("Then: 0x%X 0x%X 0x%X 0x%lX %s\n",type,u8, code, u48, atoms[atom]); 
        
        vector<SList*> args, pruned;
        for(uint64_t tofst=ofst+8; tofst < ofst + u32*8-8; tofst+=8){
           //uint64_t hofst = tofst;
           args.push_back(printins(&tofst,tstack));
           assert(tofst);
        }

#if 1
        for(auto it=args.begin(); it!=args.end(); it++){
            if(!*it || consumed.find((*it)->m_ofst) != consumed.end())
                continue;
            if((*it)->m_atom == "foreach_begin") //Check if it is a dummy atom
                continue;
            if((*it)->m_atom == "for_begin")
                continue;
            if((*it)->m_atom == "for_check")
                continue;
            if((*it)->m_atom == "foreach_check")
                continue;
            if((*it)->m_atom == "nil")
                continue;
            pruned.push_back(*it);
        }
#else
        pruned.push_back(args.back());
#endif
        if(!pruned.size()){
            printf("Hmm: %ld, %ld\n", args.size(), tstack.size());
            if(args.size())
              pruned.push_back(args.back());
            //assert(false);
        }

        SList *ret = 0;
        if(u8 == 0xb)
           ret = new SList(ofst,"then" + to_string(u32),&pruned);
        else
           ret = new SList(ofst,"else",&pruned);

        if(do_push)
           stack.push_back(ret);

        *pofst += u32*8 -8 - 8;
        return ret;
      }

      if(u8 == 0 && code == 0x3b){ //Verify fun
         //if(do_push) 
         //  stack.push_back(stack.back());
         return stack.back();
      }

      if(u8 == 0 && (code == 1 || code == 0)){
         SList *ret = 0;
         if(code == 0)
            ret = new SList(ofst,"nil");
         else
            ret = new SList(ofst,"atom_inline_" + to_string(u32));
         if(do_push)
            stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x1B){
         SList *ret = new SList(ofst,"set_sglobal");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }


      if(u8 == 0 && code == 0x21){
         SList *ret = new SList(ofst,"for_begin");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x23){
         SList *ret = new SList(ofst,"for_check");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x25){
         SList *ret = new SList(ofst,"foreach_begin");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x27){
         SList *ret = new SList(ofst,"foreach_check");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x28){
         SList *ret = new SList(ofst,"forall_begin");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x2B){
         SList *ret = new SList(ofst,"forall_check");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x2d){
         SList *ret = new SList(ofst,"exists_begin");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x2f){
         SList *ret = new SList(ofst,"exists_check");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      if(u8 == 0 && code == 0x31){
         SList *ret = new SList(ofst,"setof_begin");
         //if(do_push)
         //   stack.push_back(ret);         
         return ret;
      }

      assert(false);
      
    }else if(type == 0x1d || type == 0x3){
        printf("Load pcrel: type: 0x%X u8: 0x%X code: 0x%X u32: 0x%X @0x%lX\n",type,u8, code, u32, (ofst-arytab)/8); 
        uint64_t lofst = ofst+((int32_t)u32)*8;
        SList *ret = printins(&lofst,tstack,true);
        if(do_push)
           stack.push_back(ret);
        return ret;
    }else if(type == 0x6){
        //Load constant
        printf("Imm: 0x%X 0x%X 0x%X 0x%lX 0x%lX @0x%lX\n",type,u8, code, u48, u56, (ofst-arytab)/8); 

        SList *ret = new SList(ofst,string(to_string(((int64_t)(u56<<8))>>10)));
        if(do_push)
           stack.push_back(ret);
        return ret;
    }else if(type == 0x1a){
        //Load constant //TODO: true
        printf("Create nil 0x%X 0x%lX, 0x%X @0x%lX\n",u8, u48, code, (ofst-arytab)/8);
        assert(u8 == 0x51 || u8 == 0xB1 || u8 == 0 || u8 == 0xa2);
        SList *ret = 0;
        if(code == 0x81)
           ret = new SList(ofst,"nil");
        else
           ret = new SList(ofst,"t");

        if(do_push)
           stack.push_back(ret);
        return ret;
    }else if(type == 0xf){
        //Lots of different types of calls
        printf("Call: 0x%X 0x%X 0x%X 0x%X\n",type,u8, code, u32);
        vector<SList*> args;
        for(uint32_t i=0; i < u32; i++){
            MOV_TO_STACK(args);
        }
        reverse(args.begin(),args.end());
        printf("SCall: 0x%X 0x%X 0x%X 0x%X %s\n",type,u8, code, u32, stack.back()->m_atom.c_str());

        SList* ret=new SList(ofst,stack.back()->m_atom,&args);
        ret->m_funccall=true;
        assert(!stack.empty()); 
        stack.pop_back();
        stack.push_back(ret); 
        assert(do_push);
        return ret;
    }else if(type == 0xa){
        //Lots of different types of calls
        printf("NCall: 0x%X 0x%X 0x%X 0x%X\n",type,u8, code, u32);
        vector<SList*> args;
        MOV_TO_STACK(args);
        reverse(args.begin(),args.end());
        SList* ret=new SList(ofst,"ncall",&args);
        assert(!stack.empty()); 
        stack.pop_back();
        stack.push_back(ret); 
        assert(do_push);
        return ret;
    }else if(type == 0xd){
        //u8 is nops, u32 is pc+ofst to symbol table
        bool prog = code >> 1 == 9;

        SList* syms = new SList(0,"syms");
        vector<SList*> v;
        v.push_back(syms);
        for(uint8_t i=0;  i < u8; i++){
           uint64_t lofst = ofst+(u32+i)*8;
           SList *t = printins(&lofst,tstack,true);
           consumed.insert(t->m_ofst);
           syms->m_list.push_back(t);
        }
        printf("Let: 0x%X 0x%X 0x%X 0x%lX @0x%lX\n",type,u8, code, u48, (ofst-arytab)/8); 
        if(!prog)
           stack.resize(stack.size()-u8);
        SList *ret = new SList(ofst,prog?"prog":"let",&v);
        if(do_push)
           stack.push_back(ret); 
        return ret;
#if 0
    }else if(type == 0x9){
        printf("PutProp: 0x%X 0x%X 0x%X 0x%lX @0x%lX %s\n",type,u8, code, u48, (ofst-arytab)/8, atoms[u8]); 
        uint64_t lofst = ofst+u32*8;
        vector<SList*> tstack,args;
        SList *t = printins(&lofst,tstack,true);
        args.push_back(t);
        SList *ret = new SList(ofst,string("putpropq_") + atoms[u8],&args);
        if(do_push)
           stack.push_back(ret);
        return ret;
#endif
    }else if(type == 0x13){
        printf("Compile: 0x%X 0x%X 0x%X 0x%lX @0x%lX\n",type,u8, code, u48, (ofst-arytab)/8); 
        SList *ret = 0;
        vector<SList*> args;
        if(code == 5){
           ret = new SList(ofst,"kcompile");
           //Done
           *pofst=0;
        }else{
//           MOV_TO_STACK(args);
           ret = new SList(ofst,"compile_" + to_string(u8),&args);
        }
        if(do_push)
           stack.push_back(ret);
        return ret;
    }else if(type == 0x21){
        printf("SetVar: 0x%X 0x%X 0x%X 0x%lX @0x%lX\n",type,u8, code, u48, (ofst-arytab)/8);   

        vector<SList*> args;
        string fail="";
        for(uint32_t i=0; i < u32; i++){
            if(stack.size())
               MOV_TO_STACK(args);
            else
               fail = "fail";
        }
        reverse(args.begin(),args.end());
      
        SList *ret = new SList(ofst,"setvar_" + fail + "_" + to_string(u32) + "_" + to_string(stack.size()), &args);
        if(do_push)
           stack.push_back(ret); 
        return ret;
    }else if(type == 0x19){
        printf("DebugBreak: 0x%X 0x%X 0x%X 0x%lX @0x%lX\n",type,u8, code, u48, (ofst-arytab)/8);   
        SList *ret = new SList(ofst,"debugbreak_" + to_string(u32));
//        if(do_push)
//           stack.push_back(ret); 
        return ret;
    }else if(type == 0x1F){
        printf("LoadFunc: 0x%X 0x%X 0x%X 0x%lX @0x%lX\n",type,u8, code, u48, (ofst-arytab)/8);   

        uint64_t lofst = ofst+(u32)*8;
        SList *t = printins(&lofst,tstack,true);
        SList *ret = new SList(ofst,"loadfunc_" + to_string(u32) + "_" + t->m_atom);
        if(do_push)
           stack.push_back(ret); 
        return ret;
    }else{ 
        printf("Ukn: 0x%X 0x%X 0x%X 0x%lX 0x%X @0x%lX\n",type,u8, code, u48, u32, (ofst-arytab)/8); 
    }
    return 0;
}

void dump_func(uint64_t ofst, Func func){
#if 1
   vector<SList*> stack;
   vector<SList*> exprs;
   printf("\n\n*****Begin op dump*****\n\n");
   uint64_t nofst = ofst;//*(uint64_t*)&buf[ofst];
   SList *name = printins(&nofst,stack,true);
   printf("CD: Name %s\n", name->m_atom.c_str());
   ofst += 8;
   for(uint32_t i=0; i < func.m_args; i++){
      uint64_t nofst = ofst;//*(uint64_t*)&buf[ofst];
      SList *arg = printins(&nofst,stack,true);
      printf("CD: Arg %s\n", arg->m_atom.c_str());
      name->m_list.push_back(arg);
      ofst += 8;
   }
   SList *proc = new SList(0,"procedure");
   proc->m_list.push_back(name);

   for(uint32_t i=1+func.m_args; i < func.m_len; i++){
      SList *plist=0;
      if(plist = printins(&ofst,stack))
         exprs.push_back(plist);
      if(ofst==0)
         break;
      ofst+=8;
   }

   printf("\n\nCD:*****Begin code dump*****\n\n");
   printf("CD: Name %s\n", name->m_atom.c_str());
   vector<SList*> pruned;
   for(auto it=exprs.begin(); it!=exprs.end(); it++){
#if 1
      if(consumed.find((*it)->m_ofst) != consumed.end())
         continue;
      if(!(*it)->m_list.size())
         continue;

      pruned.push_back(*it);
   }
#endif
   for(auto it=pruned.begin(); it!=pruned.end(); it++)
      proc->m_list.push_back(*it);

   printf("CD:");
   rename("notp","!",proc);
   rename("addp","+",proc);
   rename("subp","-",proc);
   rename("divp","/",proc);
   rename("mulp","*",proc);
   rename("equalsp","==",proc);
   rename("nequalsp","!=",proc);
   rename("ltp","<",proc);
   rename("lep","<=",proc);
   rename("gtp",">",proc);
   rename("gep",">=",proc);
   rename("and","&&",proc);
   rename("or","||",proc);

   renames("setq_","setq",proc);
   rename("setq","=",proc);
   rename("getSGq","~>",proc);
   rename("range",":",proc);

   rpn("*",proc);
   rpn("+",proc);
   rpn("-",proc);
   rpn("/",proc);
   rpn("=",proc);
   rpn("~>",proc);
   rpn("==",proc);
   rpn("!=",proc);
   rpn(":",proc);
   rpn("<",proc);
   rpn("<=",proc);
   rpn(">",proc);
   rpn(">=",proc);
   rpn("&&",proc);
   rpn("||",proc);

   mov_inside("postincrement",proc);
   mov_inside("postdecrement",proc);

   rename("postincrement","++",proc);
   rename("postdecrement","--",proc);
   rename("minus","-",proc);
   renames("when_","when",proc);
   renames("if_atom_","if",proc);
   renames("then","then",proc,[](SList*t) {t->m_noparen=true;});
   renames("else","else",proc,[](SList*t) {t->m_noparen=true;});
   renames("dummy_","",proc, [](SList*t) {t->m_forcebreak=true;});
   renames("setvar_","setvar",proc);

   rot_back("setvar",&proc);
   rename("syms","",proc);

   del_to_parent("_sprintf",proc);
   insert_nil("sprintf",proc);

   print_reset();
   proc->print();
   printf("\n");
#endif
}

int main(){
   vector<uint64_t> strings, syms, lists;
   vector<Func> funcs;

   //Load entire file into memory
   FILE* f = fopen("pcellCode.cdn","r");
   fseek(f,0,SEEK_END);
   size_t sz = ftell(f);
   fseek(f,0,SEEK_SET);
   buf = (uint8_t*)valloc(sz);
   fread(buf,sz,1,f);
   fclose(f);

//   buf -= 8;
   uint64_t ofst=0;
   //Extract fields from header
   uint64_t ulong = *(uint64_t*)&buf[0x10];
   uint32_t uint = *(uint32_t*)&buf[0x18];

   printf("Long 0x%lX int 0x%X\n", ulong, uint);

   uint32_t version = *(uint32_t*)&buf[0x20];
   printf("Version 0x%X\n", version);

   uint32_t hdr_size = *(uint16_t*)&buf[0x30];

   //buf+=12;

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
       printf("Orig 0x%lx 0x%X 0x%X %X\n", orig_addr, block_size, cell_size, cell_type);
       ofst += 0x20;

       //printf("Ukn1 0x%llX\n", *(uint64_t*)ukn8);
       //assert(block_size % cell_size == 0);
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
              funcs.push_back(Func(*(uint16_t*)&buf[ofst+6], *(uint16_t*)&buf[ofst+4]));
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
 
   arytab = ofst;

#if 1
   printf("Funcs\n");
   uint64_t accum=0;
   int nfuncs=300;
   for(auto it = funcs.begin(); it!=funcs.end(); it++){
      uint64_t tofst = ofst+accum*8;
      dump_func(tofst,*it);
      accum += (*it).m_len;
      nfuncs--;
      if(!nfuncs)
        break;
   }
   exit(0);
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
