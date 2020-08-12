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

static int indent=0;
static int pos=0;
static int since_open=0;
static FILE* output_file;

set<SList*> printed;

void print_reset(FILE *f){
   indent = 0;
   pos = 0;
   output_file = f;
   printed.clear();
}

void print_token(string s, SList *t, bool dont_print){
   bool lpar = s == "(";
   bool rpar = s == ")";

   bool newline=false;

   if(s.rfind("dangling",0)==0 && s.rfind("dangling_10065",0) && s.rfind("dangling_1002d",0) && s.rfind("dangling_1006d",0)){
#if 0
      printf("%s\n", s.c_str());
      assert(false);
#endif
   }

   if(pos > 80 || s == "setq" || s == "foreach" || s == "let" || s == "putpropq" 
          || s == "for" || s == "compile" || s == "dbCloseBag" || s == "if" || s == "else" 
          || s == "return" || s == "case" || s == "nil" || s == "prog" || s == "unless"
          || s == "list" || s == "cond" || s == "property" || s == "dbReplaceProp"
          || s.rfind("setvar",0)==0 || s.rfind("if",0)==0 || s.rfind("when",0)==0 
          || s.rfind("then",0)==0 || s.rfind("loadfunc",0)==0
          || s.rfind("compile",0)==0 || s.rfind("while",0)==0 || s.rfind("foreach",0)==0
          || s.rfind("ts",0)==0 || (t && lpar && t->m_list.size() > 1 && (
              t->m_list[1]->m_atom == "=" 
              || t->m_list[1]->m_atom == "=="
              || t->m_list[1]->m_atom == ">="
              || t->m_forcebreak
          )) || (t && s == t->m_atom && t->m_funccall)){
      printf("\nCD: ");
      if(output_file)
         fprintf(output_file,"\n");
      for(int i=0; i < indent; i++){
         printf("   ");
         if(output_file)
            fprintf(output_file,"   ");
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
       if(output_file)
          fprintf(output_file," ");
     }
     since_open++;
   }
   pos += s.size();
   if(!dont_print){
      printf("%s", s.c_str());
      if(output_file)
         fprintf(output_file,"%s", s.c_str());
   }else{
      printf(" ");
      if(output_file)
         fprintf(output_file," ");
   }
}
