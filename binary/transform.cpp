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

void findAndReplaceAll(std::string & data, std::string toSearch, std::string replaceStr) {
    size_t pos = data.find(toSearch);
    while( pos != std::string::npos) {
	data.replace(pos, toSearch.size(), replaceStr);
	pos =data.find(toSearch, pos + replaceStr.size());
    }
}

string escape(string s){
   if(s[0] == '"'){
      findAndReplaceAll(s,"\n","\\n");
   }else{
      if(s.size() > 1)
         findAndReplaceAll(s,"-","\\-");
   }
   return s;
}

void rename(string a, string b, SList *l){
    if(l->m_atom == a)
      l->m_atom = b;
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          rename(a,b,*it);
}

void del_to_parent(string a, SList *l){
   if(l->m_list.size() == 1){
       if(l->m_list[0]->m_atom == a){
          l->m_list = l->m_list[0]->m_list;
       }
   }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          del_to_parent(a,*it);

}


void renames(string a, string b, SList *l, void(*lambda)(SList*)){
    if(l->m_atom.rfind(a,0) == 0){
      l->m_atom = b;
      if(lambda)
        (*lambda)(l);
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          renames(a,b,*it,lambda);
}


void rpn(string a, SList *l){
    if(l->m_atom == a && l->m_list.size()){
      l->m_atom = "";
      vector<SList*> new_list;
      new_list.push_back(l->m_list.front());
      for(auto it=next(l->m_list.begin(),1); it!=l->m_list.end(); it++){
          new_list.push_back(new SList(0,a));
          new_list.push_back(*it);
      }
      l->m_list = new_list;
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          rpn(a,*it);
}

void mov_inside(string a, SList *l){
    if(l->m_atom == a && l->m_list.size()){
      l->m_atom = "";
      vector<SList*> new_list;
      new_list.push_back(l->m_list.front());
      new_list.push_back(new SList(0,a));
      l->m_list = new_list;
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          mov_inside(a,*it);
}

void rot_back(string a, SList **pl){
    SList *l = *pl;
    if(l->m_atom == a){
       SList *nl = l->m_list[0];
       nl->m_list.push_back(l);
       l->m_list.erase(l->m_list.begin());
       l->m_atom = "";
       l->m_noparen=true;
       *pl = nl;
       l=nl;
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          rot_back(a,&(*it));

}

void insert_nil(string a, SList *l){
    if(l->m_atom == a){
        l->m_list.insert(l->m_list.begin(),new SList(0,"nil"));
    }
    for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          insert_nil(a,*it);
}

