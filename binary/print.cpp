#include "main.h"

static int indent=0;
static int pos=0;
static int since_open=0;
void print_reset(){
   indent = 0;
   pos = 0;
}

void print_token(string s){
   bool lpar = s == "(";
   bool rpar = s == ")";

   bool newline=false;
   if(pos > 80 || s == "setq" || s == "foreach" || s == "let" || s == "putpropq" 
          || s == "for" || s == "compile" || s == "dbCloseBag" || s == "if" || s == "else" 
          || s == "return"
          || s.rfind("setvar",0)==0 || s.rfind("if",0)==0 || s.rfind("when",0)==0 
          || s.rfind("then",0)==0 || s.rfind("rod",0)==0){
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
   printf("%s", s.c_str());
}
