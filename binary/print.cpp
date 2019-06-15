#include "main.h"

static int indent=0;
static int pos=0;
static int since_open=0;
void print_reset(){
   indent = 0;
   pos = 0;
}

void print_token(string s, SList *t, bool dont_print){
   bool lpar = s == "(";
   bool rpar = s == ")";

   bool newline=false;
   if(pos > 80 || s == "setq" || s == "foreach" || s == "let" || s == "putpropq" 
          || s == "for" || s == "compile" || s == "dbCloseBag" || s == "if" || s == "else" 
          || s == "return" || s == "case" || s == "nil"
          || s.rfind("setvar",0)==0 || s.rfind("if",0)==0 || s.rfind("when",0)==0 
          || s.rfind("then",0)==0 || s.rfind("rod",0)==0 || s.rfind("loadfunc",0)==0 || s.rfind("db",0)==0 
          || s.rfind("dummy",0)==0 
          || s.rfind("ts",0)==0 || (lpar && t->m_list.size() > 1 && (
              t->m_list[1]->m_atom == "=" 
              || t->m_list[1]->m_atom == "=="
              || t->m_list[1]->m_atom == ">="
              || t->m_forcebreak
          ))){
      printf("\nCD: ");
      for(int i=0; i < indent; i++){
         printf("   ");
      }
      pos = indent*3;
      newline=true;
   }

   if(lpar){
     indent++;
     since_open=0;
   }else if(rpar)
     indent--;
   else{
     if(since_open && !newline){
       pos += 1;
       printf(" ");
     }
     since_open++;
   }
   pos += s.size();
   if(!dont_print)
      printf("%s", s.c_str());
}
