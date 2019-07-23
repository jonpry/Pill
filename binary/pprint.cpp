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

enum { STATE_NONE, STATE_ML, STATE_COMMENT, STATE_STRING };

void emit(string s){
   //printf("Emit: %s\n", s.c_str());
   print_token(s,0,false);
}

int main(int argc, char** argv){
   //Load entire file into memory
   if(argc != 3){
      printf("Usage: ./pprint INFILE OUTFILE\n");
      exit(0);
   }

   FILE* f = fopen(argv[1],"r");
   if(!f){
       printf("Could not open file %s\n", argv[1]);
       exit(0);
   }

   FILE* of = fopen(argv[2],"w+");
   if(!of){
       printf("Could not open file %s\n", argv[2]);
       exit(0);
   }


   fseek(f,0,SEEK_END);
   size_t sz = ftell(f);
   fseek(f,0,SEEK_SET);
   uint8_t *buf = (uint8_t*)valloc(sz);
   fread(buf,sz,1,f);
   fclose(f);

   print_reset(of);

   int state = STATE_NONE;
   char prev_token=0;
   bool had_slash=false;
   string s="";
   for(size_t i=0; i < sz; i++){
      char token = buf[i];
      switch(state){
         case STATE_NONE: {
               if(token == '/'){
                  had_slash=true;
                  break;
               }
               if(had_slash){
                  had_slash=false;
                  if(s != ""){
                     emit(s);
                     s="";
                  }
                  if(token == '*'){
                     state = STATE_ML;
                     break;
                  }
                  emit("/");
                  break;
               }
               if(token == ';'){
                  if(s != ""){
                     emit(s);
                  }
                  s = ";";
                  state = STATE_COMMENT;
                  break;
               }
               if(token == '\"'){
                  if(s != ""){
                     emit(s);
                  }
                  s = "";
                  state = STATE_STRING;
                  break;
               }
               if(isalnum(token) || token=='.' || token=='-' || token=='+' 
                     || token=='_' || token=='~' || token=='>' || token=='!' 
                     || token=='=' || token=='|' || token=='&' || token=='\''){
                  s = s + token;
                  break;
               }

               if(s != ""){
                  emit(s);
                  s="";
               }

               if(token != ' ')
                  emit(string("") + token);
               
            } break;       
         case STATE_ML: {
              if(token == '/' && prev_token == '*')
                 state = STATE_NONE;
            } break;  
         case STATE_COMMENT: {
              s = s + token;
              if(token == '\n'){
                 state = STATE_NONE;
                 emit(s);
                 s = "";
              }
            } break;  
         case STATE_STRING: {
              s = s + token;
              if(had_slash){
                 had_slash=false;
                 break;
              }
              if(token == '\\'){
                 had_slash=true;
                 break;
              }    
              if(token == '\"'){
                 state = STATE_NONE;
                 emit("\"" + s);
                 s = "";
              }
            } break;
      }
      prev_token = token;
   } 

   fclose(of);
}
