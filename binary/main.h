#pragma once

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

using namespace std;

class SList;

extern set<uint64_t> consumed;

void print_token(string s, SList *t,bool dont_print=false);
void print_reset();

template <typename T>
string to_scientific(const T a_value, const int n = 11)
{
    ostringstream out;
    out.precision(n);
    out << scientific << a_value;
    return out.str();
}

class SList {
 public:
   SList(uint64_t ofst, string atom="", vector<SList*> *slist=0){
      m_atom = atom;
      m_forcebreak=false;
      m_noparen=false;
      assert(m_atom.size());
      m_ofst = ofst;
      if(slist){
         m_list = *slist;  
         for(auto it=m_list.begin(); it!=m_list.end(); it++){
            if(*it)
               consumed.insert((*it)->m_ofst);
         }
      }
   }

   void print(){
     if(m_atom.size())
        print_token(m_atom,this);
     else
        print_token(" ",this);
     if(m_list.size())
        print_token("(",this,m_noparen);
     else 
        if(!m_atom.size()){
           print_token("nil",this);
        }
     for(auto it=m_list.begin(); it!=m_list.end(); it++){
        if(*it)
           (*it)->print();
        else
           print_token("NULLPTR!!!!",this);
     }
     if(m_list.size())
        print_token(")",this,m_noparen);
   }

   uint64_t m_ofst;
   string m_atom;
   bool m_forcebreak, m_noparen;
   vector<SList*> m_list;
};

class Func {
 public:
   Func(uint32_t len, uint32_t n_args) : m_len(len), m_args(n_args) {}

   uint32_t m_len, m_args;
};

void rename(string a, string b, SList *l);
void renames(string a, string b, SList *l, void(*lambda)(SList*) =0);

void rpn(string a, SList *l);
void mov_inside(string a, SList *l);
void rot_back(string a, SList **l);

