#pragma once
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


#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <sstream>
#include <functional>
#include <iostream>

#include <filesystem>

#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))


using namespace std;
namespace fs = std::filesystem;

class SList;

extern set<uint64_t> consumed;
extern set<SList*> printed;
extern map<uint64_t,SList*> frompos;


void print_token(string s, SList *t,bool dont_print=false);
void print_reset(FILE *f);

string escape(string s);

template <typename T>
string to_scientific(const T a_value, const int n = 11)
{
    ostringstream out;
    out.precision(n);
    out << scientific << a_value;
    return out.str();
}


static string to_hex(uint64_t to_convert){
    std::string result;
    std::stringstream ss;
    ss << std::hex <<to_convert;
    ss >> result;
    return result;
}

class SList {
 public:
   SList(uint64_t ofst, string atom="", vector<SList*> *slist=0){
      frompos[ofst] = this;
      m_atom = atom;
      m_forcebreak=false;
      m_noparen=false;
      m_funccall=false;
      m_forceparen=false;
      m_ofst = ofst;
      m_escape=true;
      m_tgt = 0;
      if(slist){
         m_list = *slist;  
         for(auto it=m_list.begin(); it!=m_list.end(); it++){
            if(*it)
               consumed.insert((*it)->m_ofst);
         }
      }
   }

   SList(bool has_tgt, uint64_t tgt){
      m_tgt = tgt;
      m_atom = "dangling_" + to_hex(tgt);
   }


   ~SList(){
      for(auto it=m_list.begin(); it!=m_list.end(); it++){
         if(*it)
           delete *it;
      }
   }

   void print(set<SList*> *stack=0){
     printed.insert(this);
     if(m_atom.size()){
        if(m_escape)
           print_token(escape(m_atom),this);
        else
           print_token(m_atom,this);
     }else
        print_token(" ",this);
     if(m_list.size() || m_forceparen)
        print_token("(",this,m_noparen);
     else 
        if(!m_atom.size()){
           print_token("nil",this);
        }
     if(stack)
        stack->insert(this);
     for(auto it=m_list.begin(); it!=m_list.end(); it++){
        if(*it){
           if(*it != this)//printed.find(*it)==printed.end())
              if(stack->find(*it) == stack->end())
                 (*it)->print(stack);
              else
                 print_token("CIRC!!!!",this);
           else
              print_token("SELF!!!!",this);
        }else
           print_token("NULLPTR!!!!",this);
     }
     if(stack)
        stack->erase(this);
     if(m_list.size() || m_forceparen)
        print_token(")",this,m_noparen);
   }

   uint64_t m_ofst, m_tgt;
   string m_atom;
   bool m_forcebreak, m_noparen, m_funccall, m_forceparen, m_escape;
   vector<SList*> m_list;
   map<string,SList*> m_map;
};

class Func {
 public:
   Func(uint32_t len, uint32_t n_args) : m_len(len), m_args(n_args) {}

   uint32_t m_len, m_args;
};

string format_double(double d);

void rename(string a, string b, SList *l, void(*lambda)(SList*) =0);
void renames(string a, string b, SList *l, void(*lambda)(SList*) =0);

void rpn(string a, SList *l,bool reverse=false);
void mov_inside(string a, SList *l);
void mov_inside_front(string a, SList *l);
void del_to_parent(string a, SList *l);
void rot_back(string a, SList **pl, set<SList*> *parents =0);
void insert_nil(string a, SList *l, void(*lambda)(SList*) =0);
void setsgq(SList *l);
void putpropq(SList *l);
void condfix(SList *l);
void forfactor(SList *l);
void arrayfix(SList *l);
void callablefix(SList *l);
void foreachfactor(string a, SList *l);
void postfactor(SList *l);
void elsefix(SList *l);
void popback(string a, SList *l);

SList* staticfactor(SList *l,bool quoted=false);

