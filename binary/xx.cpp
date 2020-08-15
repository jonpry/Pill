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

set<uint64_t> consumed;
map<uint64_t,SList*> frompos;

static bool big_endian;

#define __nswap_16(x) (big_endian?__bswap_16(x):x)
#define __nswap_32(x) (big_endian?__bswap_32(x):x)
#define __nswap_64(x) (big_endian?__bswap_64(x):x)


/*  Sizes64
Type Name		Type Id		Size in bytes
----------		--------	-------------
char            	     0			 1
char            	     1			 1
short           	     2			 2
short           	     3			 2
int             	     4			 4
int             	     5			 4
long            	     6			 8
long            	     7			 8
float           	     8			 4
float           	     9			 4
double          	    10			 8
double          	    11			 8
pointer         	    12			 8
pointer         	    13			 8
byte            	    14			 1
byte            	    15			 1
XXrcb           	    16			48
XXfreeObject2   	    18			 8
XXfreeObject    	    19			16
XXproperty      	    20			40
XXrange         	    21			32
XXgroup         	    22			32
XXgroupMember   	    23			40
XXilSymbol      	    32			 8
XXilList        	    33			16
dbPoint         	    34			 8
dbPoint         	    35			 8
dbBBox          	    36			16
dbBBox          	    37			16
XXparentChild   	    38			16
XXSstring       	    40			 4
zeCellView      	    50			88
zeOldInstHeader 	    51			104
zeLP            	    52			40
zeOldFig        	    60			48
zeInst          	    61			40
ze2OldMosaic    	    62			72
zeMosaicTile    	    63			 2
zeMosaicTile    	    64			 2
zeLabel         	    65			32
zeArc           	    66			40
zeDonut         	    67			16
zePolygon       	    68			12
zeOrthPolygon   	    69			16
zeLine          	    71			12
zePath          	    74			24
zeNet           	    80			64
zeSig           	    81			32
zeTerm          	    82			40
zePin           	    83			40
zeInstTerm      	    84			40
zeInstPin       	    85			24
zeOldNetFig     	    86			16
zePhysConn      	    87			40
zeOldMosaic     	    88			72
zeFig           	    89			56
zeOldTextDisplay	    90			48
zeTextDisplay   	    91			80
zeInstHeader    	    92			104
zeMosaic        	    93			72
zeAnyInst       	    94			56
zeMagInst       	    95			16
zeLrgSigAryInfo 	    96			 8
*/

const char* types[] = {"char", "char", "short", "short",
                       "int", "int", "long", "long",
                       "float", "float", "double", "double",
                       "pointer", "pointer", "byte", "byte",


                       "XXrcb", "XXfreeObject2", "XXfreeObject", "XXproperty",
                       "XXrange", "XXgroup", "XXgroupMember", 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0,

                       "XXilSymbol", "XXilList", "dbPoint", "dbPoint",
                       "dbBBox", "dbBBox", "XXparentChild", 0,
                       "XXSstring", 0, 0, 0,
                       0,0,0,0,

                       0,0,"zeCellView", "zeOldInstHeader",  //48
                       "zeLP", 0, 0, 0,
                       0, 0, 0, 0,
                       "zeOldFig", "zeInst", "ze2OldMasic", "zeMosaicTile",

                       "zeMosaicTile", "zeLabel", "zeArc", "zeDonut", //64
                       "zePolyon", "zeOrthPolygon", 0, "zeLine",
                       0, 0, "zePath", 0,
                       0, 0, 0, 0,

                       "zeNet", "zeSig", "zeTerm", "zePin",
                       "zeInstTerm", "zeInstPin", "zeOldNetFig", "zePhysConn",
                       "zeOldMosaic", "zeFig", "zeOldTextDisplay", "zeTextDisplay",
                       "zeInstHeader", "zeMosaic", "zeAnyInst", "zeMagInst",

                       "zeLrgSigAryInfo"};


uint32_t sizes32[] = { 4, 1, 2, 2, 4, 4, 4, 4,  //0
                     4, 4, 8, 8, 4, 4, 1, 1,  //8
                     0x24, 0, 4, 0x8, 0x14, 0x10, 0x10, 0x14, //0x10
                     0, 0, 0, 0, 0, 0, 0, 0, //0x18
                     4, 8, 8, 8, 0x10, 0x10, 8, 0, //0x20
                     4, 0, 0, 0, 0, 0, 0, 0, //0x28
                     0, 0, 0xc, 0x44, 0x1c, 0, 0, 0, //0x30
                     0, 0, 0, 0, 0x20, 0x1c, 0x30, 2,
                     2, 0x14, 0x28, 0x10, 0xc, 0x10, 0, 0xc,
                     0, 0, 0x18, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0x20, 0x10, 0x14, 0x14,
                     0x14, 0xc, 8, 0x14, 0x30, 0x20, 0x1c, 0x2c,
                     0x44, 0x30, 0x20, 8};


uint32_t sizesc32[] = { 4, 1, 4, 2, 4, 4, 4, 4,  //0
                     4, 4, 8, 8, 4, 4, 1, 1,  //0x8
                     0x24, 0, 4, 0x8, 0xe, 0x10, 0x9, 0x10, //0x10
                     0, 0, 0, 0, 0, 0, 0, 0, //0x18
                     4, 8, 8, 8, 0x10, 0x10, 8, 0, //0x20
                     4, 0, 0, 0, 0, 0, 0, 0, //0x28
                     0, 0, 0x110-0xe8-4, 0x44, 0xe, 0, 0, 0, //0x30
                     0, 0, 0, 0, 0x20, 0x1c, 0x30, 2, //0x38
                     2, 0x14, 0x28, 0x10, 0xc, 0x10, 0, 0x1c, //0x40
                     0, 0, 0x18, 0, 0, 0, 0, 0, //0x48
                     0x1a7, 8, 40, 40, 0x20, 0x10, 0x14, 0x14, //0x50
                     0x14, 0xc, 8, 0x14, 0x30, 0x20, 0x1a, 0x2c,//0x58
                     0x44, 0x30, 0x20, 8};

set<uint32_t> arrayTypes = {1,3,5,7,9,11,13,15,35,37,64};

string prop_types[] = { "uknown", "string", "int", "float", "bool", "time", "file", "expr", "nexpr", "hier", "list", "net"};

#define MIN(a,b) ((a)<(b)?(a):(b))

void printbytes(uint8_t *buf, uint32_t len){
   for(uint32_t i=0; i < len+8; i+=16){
      printf("%4.4X: ", i);
      for(uint32_t j=i; j < MIN(i+16,len+8); j++){
         if(j==len)
            printf("|| ");
         printf("%2.2X ", buf[j]);
      }
      printf("\n");
   }
}

void parseseg(uint8_t* buf, uint32_t seg_start, uint32_t pos, uint32_t i, uint32_t b){
       #if 1

       //Some kind of element header
       //if(i==0)
       while(b>0){
       uint32_t type = __nswap_16(*(uint16_t*)&buf[pos+2]) & 0xFF;
       if(type>96 || !type)
          return;

       uint32_t esz = sizes32[type];

       uint32_t nelem=1; //if !arrayType

       uint32_t rel_pos = ((i+1)<<16) + pos-seg_start - 0x40 + 0x4 + 1;
       printf("El Type: %x %dd,%s, TS: %d@%x:%x  %x\n", type, type, types[type], esz, rel_pos+(type==1?8:0),pos, __nswap_32(*(uint32_t*)&buf[pos]));
       assert(*(uint16_t*)&buf[pos] == 0);

       //assert(typeMap.find(type) != typeMap.end());

       pos+=0x4;
       b-=0x4;

       if(arrayTypes.find(type)!=arrayTypes.end()){
          esz = __nswap_32(*(uint32_t*)&buf[pos]) - 4;
          rel_pos+=8;
          if(type==1){ //string
             printf("String: %x %s\n", esz, &buf[pos+8]);
             new SList(rel_pos,"\"" + string((char*)&buf[pos+8]) + "\"");
          }
       }

       if(type==32){
            uint32_t aloc = __nswap_32(*(uint32_t*)&buf[pos]) &0xFFFFF;
            printf("Aloc: %X\n", aloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            new SList(rel_pos,"symbol",&args);
       }

       if(type==4){
            int32_t aloc = __nswap_32(*(int32_t*)&buf[pos]);
            new SList(rel_pos,to_string(aloc));
       }

       if(type==0){
            int8_t aloc = *(int8_t*)&buf[pos];
            new SList(rel_pos,to_string(aloc));
       }

       if(type==10){
            uint64_t aloc = __bswap_64(*(uint64_t*)&buf[pos]);
            double d = *(double*)&aloc;
            new SList(rel_pos,format_double(d));
       }

       if(type==19){
            uint32_t aloc = __nswap_32(*(uint32_t*)&buf[pos]);
            esz += __nswap_32(*(uint32_t*)&buf[pos+4])*4;
            printf("Aloc: %X\n", aloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            new SList(rel_pos,"freeObject",&args);
       }


       if(type==20){
            uint32_t aloc = __nswap_32(*(uint32_t*)&buf[pos]);
            uint32_t bloc = __nswap_32(*(uint32_t*)&buf[pos+0xc]);
            uint32_t cloc = __nswap_32(*(uint32_t*)&buf[pos+0x10]);
            uint32_t dloc = __nswap_32(*(uint32_t*)&buf[pos+4]);
            uint8_t ptype = buf[pos+8];

            printf("Aloc: %X %X %X %X %X\n", aloc, bloc, cloc, dloc, ptype);
            vector<SList*> args;
            if(aloc < 0x10000){
                esz-=8;
                args.push_back(new SList(true,dloc));
                new SList(rel_pos+4,"property",&args);
            }else{
               if(aloc)
                  args.push_back(new SList(true,aloc));
               if(ptype == 3){
                  if(bloc)
                    args.push_back(new SList(0,"t"));
                  else
                    args.push_back(new SList(0,"nil"));
               }else if(ptype == 1){
                  args.push_back(new SList(0,to_string(bloc)));
               }else{
                  if(bloc && !(bloc>>24))
                     args.push_back(new SList(true, bloc));
               }
               if(cloc)
                  args.push_back(new SList(true, cloc));
               new SList(rel_pos,"property",&args);
            }
        }

       if(type==21){ //range
            uint32_t aloc = __nswap_32(*(uint32_t*)&buf[pos+4]);
            uint32_t bloc = __nswap_32(*(uint32_t*)&buf[pos+8]);
            vector<SList*> args;

            if(aloc)
               args.push_back(new SList(true,aloc));
            if(bloc)
               args.push_back(new SList(true, bloc));
            new SList(rel_pos,"range",&args);

        }

        if(type==33){
            uint32_t aloc = __nswap_32(*(uint32_t*)&buf[pos]);
            uint32_t bloc = __nswap_32(*(uint32_t*)&buf[pos+4]);
            printf("Aloc: %X %X\n", aloc, bloc);
            vector<SList*> args;
            if(aloc)
               args.push_back(new SList(true,aloc));
            else
               args.push_back(new SList(0,"nil"));
            if(bloc)
               args.push_back(new SList(true, bloc));
            else
               args.push_back(new SList(0,"nil"));
            new SList(rel_pos,"list_node",&args);
        }

        if(type==50){
            new SList(rel_pos,"zeCellView");//TODO: don't know if multiple can exist in single file
        }

        if(frompos.find(rel_pos) == frompos.end()){
            new SList(rel_pos,string("unknown_") + types[type]);
        }

        printbytes(&buf[pos], esz);

        pos+=esz;
        b-=esz;
     }
}

SList* consume_pointer(uint32_t *pos, int32_t *b, uint8_t *buf, bool force=false, uint32_t *rel_pos=0){
   SList *ret=0;
   uint16_t seg = __nswap_16(*(uint16_t*)&buf[*pos]);
   uint16_t ofs = __nswap_16(*(uint16_t*)&buf[(*pos)+2]);

   if(seg || force){
      uint32_t aloc = (seg << 16) + ofs;
      *pos+=4;
      *b-=4;
      ret = new SList(true,aloc);
   }else{
      *pos+=2;
      *b-=2;
      ret = new SList(0,"nil");
   }

   if(rel_pos){
     *rel_pos += 4;
   }

   return ret;
}

SList* consume_u32(uint32_t *pos, int32_t *b, uint8_t *buf){
   uint32_t aloc = __nswap_32(*(uint32_t*)&buf[*pos]);
   *pos+=4;
   *b-=4;
   return new SList(0,"0x" + to_hex(aloc));
}

SList* consume_u16(uint32_t *pos, int32_t *b, uint8_t *buf){
   uint32_t aloc = __nswap_16(*(uint16_t*)&buf[*pos]);
   *pos+=2;
   *b-=2;
   return new SList(0,"0x" + to_hex(aloc));
}

SList* consume_s32(uint32_t *pos, int32_t *b, uint8_t *buf){
   int32_t aloc = __nswap_32(*(int32_t*)&buf[*pos]);
   *pos+=4;
   *b-=4;
   SList* ret=new SList(0,to_string(aloc));
   ret->m_escape=false;
   return ret;
}

SList* consume_byte(uint32_t *pos, int32_t *b, uint8_t *buf, bool decimal=false){
   *pos+=1;
   *b-=1;
   if(decimal)
       return new SList(0,to_string(buf[*pos-1]));
   return new SList(0,string("byte_") + to_string(buf[*pos-1]));
}

map<int,string> fig_type_map = {
                      {0, "label"},
                      {5, "rect"},
                      {6, "polygon"},
                      {7, "line"},
                      {8, "path"},
                      {0xa, "label"}, //TODO: Maybe pin or something
                      {0xb, "ellipse"},
                      {0xc, "donut"},
                      {0xd, "mosaic"},
                      {0xf, "maginst"},
                      {0x1a, "dot"},
                      {0x21, "textdisplay"}};
                     //TODO: 0x22-0x25 are some kind of manhattan distance thing


void parsecseg(uint8_t* buf, uint32_t seg_start, uint32_t pos, uint32_t i, int32_t b, const char* fname){
       //Some kind of element header
       //if(i==0)
   uint32_t rel_pos = ((i+1)<<16)+1;
   uint32_t cnt=0;
   while(b>0){
       vector<SList*> args;
       uint32_t opos=pos;

       uint32_t type = buf[pos];
       if(type>96){// || !type){
          printf("Bad type %x %d\n", type, type);
          //exit(0);
          assert(false);
          return;
       }

       uint32_t esz = sizesc32[type];

       uint32_t nelem=1; //if !arrayType

       if(cnt++ == 2 && i == 0)
          rel_pos += 0x38;
       rel_pos+=4;

       printf("El Type: %x,%s, TS: %d@%x:%x  %x in %s\n", type, types[type], esz, (type==0x1?8:0)+rel_pos,pos, __nswap_32(*(uint32_t*)&buf[pos]), fname);

       //assert(typeMap.find(type) != typeMap.end());

       pos+=0x1;
       b-=0x1;
       int32_t extra=0;

       if(type==37){ //dbbox array
           esz=0;
           args.push_back(consume_pointer(&pos,&b,buf));
       }else if(arrayTypes.find(type)!=arrayTypes.end()){
          esz = __nswap_16(*(uint16_t*)&buf[pos]) - 12;
          pos+=2;
          b-=2;

          if(type==0xd){
             for(uint32_t i=0; i < esz/4; i++)
                args.push_back(consume_pointer(&pos,&b,buf));
             new SList(rel_pos+8,"pointer",&args);
          }else{
             if(type==1){ //string
                printf("String: %dd %s\n", esz, &buf[pos]);
                new SList(rel_pos+8,"\"" + string((char*)&buf[pos]) + "\"");
             }
             pos+=esz;
             b-=esz;
          }
          if(__nswap_16(*(uint16_t*)&buf[opos+1])-4 > 0xC)
             rel_pos+=__nswap_16(*(uint16_t*)&buf[opos+1])-4;
          else
             rel_pos+=0xc;
          //rel_pos+=esz+8;
          esz=0;
          printbytes(&buf[opos], esz+(pos-opos));
          continue;
      }else if(type==0){ //char
            int8_t aloc = *(int8_t*)&buf[pos];
            esz=1;
            new SList(rel_pos,to_string(aloc));
            extra=4;
       }else if(type==4){ //int
            int32_t aloc = __nswap_32(*(int32_t*)&buf[pos]);
            new SList(rel_pos,to_string(aloc));
       }else if(type==10){ //double
            uint64_t aloc = __bswap_64(*(uint64_t*)&buf[pos]);
            uint32_t bloc = __nswap_32(*(uint32_t*)&buf[pos]);
            double d = *(double*)&aloc;
            printf("D: %lX S: %X %.14g %f\n", aloc, bloc, d, *(float*)&bloc);
            new SList(rel_pos,format_double(d));
       }else if(type==12){ //pointer
           esz=0;
           args.push_back(consume_pointer(&pos,&b,buf,true));
       }else if(type==16){//rcb
           esz=0;
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_pointer(&pos,&b,buf,true));
           args.push_back(consume_byte(&pos,&b,buf));
           args.push_back(consume_byte(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_u32(&pos,&b,buf));
           args.push_back(consume_pointer(&pos,&b,buf));
           args.push_back(consume_pointer(&pos,&b,buf));
           args.push_back(consume_pointer(&pos,&b,buf,true));
           new SList(rel_pos,"rcb",&args);

           rel_pos+=0x24;
           printbytes(&buf[opos], esz+(pos-opos));
           continue;
       }else if(type==18){
           esz=0;
           extra=4;
       }else if(type==19){ //freeobject
           esz=4;
           extra=4;
           uint32_t free = __nswap_32(*(uint32_t*)&buf[pos]);
           extra += 4 * free;
       }else if(type==20){ //property
            esz=0;
            uint32_t orel_pos = rel_pos;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            uint8_t ptype = buf[pos++];
            b-=1;
            args.push_back(new SList(0,string("type_") + to_hex(ptype)));
            args.push_back(consume_byte(&pos,&b,buf));
            if(ptype==0xa){
               args.push_back(consume_pointer(&pos,&b,buf,true));
               //extra+=3;
               //rel_pos+=4;
            }else{
               if(ptype==0 || ptype == 0xd || ptype == 4 || ptype == 7)
                  args.push_back(consume_pointer(&pos,&b,buf,true));
               else
                  args.push_back(consume_u32(&pos,&b,buf));
               args.push_back(consume_pointer(&pos,&b,buf));
               //extra+=6;
            }

            printf("Prop type: %x %s\n", ptype, prop_types[ptype].c_str());
#if 1
            new SList(orel_pos,"property",&args);

            rel_pos+=0x14;
            printbytes(&buf[opos], esz+(pos-opos));
            continue;
#endif
        }else if(type==21){//range

            esz=0;
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            new SList(rel_pos,"range",&args);

            extra=0x4;//0x10;
        }else if(type==22){
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"group",&args);

            extra=9;
        }else if(type==23){
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.clear();
            new SList(rel_pos,"group_member",&args);

            extra=4;
        }else if(type==32){
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"symbol",&args);
        }else if(type==33){
            esz=0;
            uint32_t orel_pos = rel_pos;
            args.push_back(consume_pointer(&pos,&b,buf,false,&rel_pos));
            args.push_back(consume_pointer(&pos,&b,buf,false,&rel_pos));
            new SList(orel_pos,"list_node",&args);

            printbytes(&buf[opos], esz+(pos-opos));
            continue;
        }else if(type==38){ //XXparentChild
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"parent_child",&args);
        }else if(type==52){ //zeLP
            esz=0;
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf,true)); //purpose
            args.push_back(consume_byte(&pos,&b,buf,true)); //layer
            consume_pointer(&pos,&b,buf); //Linked list
            args.push_back(consume_u32(&pos,&b,buf));

            new SList(rel_pos,"LP",&args);
            extra=0x10;
        }else if(type==65){ //zeLabel
            esz=0;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_s32(&pos,&b,buf));
            args.push_back(consume_s32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            new SList(rel_pos,"label",&args);
        }else if(type==66){ //zeArc
            esz=0;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            new SList(rel_pos,"arc",&args);
            extra=0x10;
        }else if(type==68){
            esz=0;
            uint32_t cnt = __nswap_32(*(uint32_t*)&buf[pos]);
            pos+=4;
            b-=4;
            for(uint32_t j=0; j < cnt; j++){
               vector<SList*> pargs;
               pargs.push_back(consume_s32(&pos,&b,buf));
               pargs.push_back(consume_s32(&pos,&b,buf));
               args.push_back(new SList(0,"",&pargs));

            }
            new SList(rel_pos,"polygon",&args);
        }else if(type==71){ //zeLine
            esz=0;
            uint32_t pcnt = __nswap_32(*(uint32_t*)&buf[pos]);
            pos+=4;
            b-=4;
            for(uint32_t i=0; i < pcnt; i++){
               args.push_back(consume_u32(&pos,&b,buf));
               args.push_back(consume_u32(&pos,&b,buf));
            }
            new SList(rel_pos,"line",&args);

        }else if(type==74){ //zePath
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            esz=0;
            uint32_t cnt = __nswap_16(*(uint16_t*)&buf[pos]);
            pos+=2;
            b-=2;


            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            for(uint32_t j=0; j < cnt; j++){
               args.push_back(consume_s32(&pos,&b,buf));
               args.push_back(consume_s32(&pos,&b,buf));
            }
            new SList(rel_pos,"path",&args);
            extra+=2;
        }else if(type==80){ //zeNet
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            extra+=0x14;
            new SList(rel_pos,"net",&args);

       }else if(type==81){ //zeSig
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));
            extra += 8;
            new SList(rel_pos,"sig",&args);
        }else if(type==82){ //zeTerm
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            new SList(rel_pos,"term",&args);
            extra+=0x9;
        }else if(type==83){ //zePin
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            extra+=4;
            new SList(rel_pos,"pin",&args);
        }else if(type==84){ //zeInstTerm
            esz=0;
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));

            extra=0x8;
        }else if(type==89){ //zeFig
            esz=0;
            uint8_t ftype = buf[pos];
            pos++;
            b--;
            args.push_back(consume_byte(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf,true));
            args.push_back(consume_byte(&pos,&b,buf,true));

            printf("FIG %x\n", ftype);

//0000: 59 0A FC E6 00 00 05 0A 59 00 01 00 2D 59 05 FC 09 00 00 00 1B **58 00 00 05

            if(ftype==5 || ftype == 0x22 || ftype==0x1a || ftype==0xb || ftype==0x23 || ftype==0x24 || ftype==0x25){
               vector<SList*> rargs;
               for(uint32_t j=0; j < 4; j++){
                  rargs.push_back(consume_s32(&pos,&b,buf));
               }
               args.push_back(new SList(0,"bbox",&rargs));
               consume_pointer(&pos,&b,buf,true); //TODO: LP
            }else if(ftype==9 || ftype==0x21 || ftype==0xd){
               for(uint32_t j=0; j < 6; j++){
                  args.push_back(consume_u32(&pos,&b,buf));
               }
            }else{
               args.push_back(consume_pointer(&pos,&b,buf,true));
               consume_pointer(&pos,&b,buf,true); //TODO: self and linked list stuff
            }

            if(fig_type_map.find(ftype) == fig_type_map.end()){
               printf("Unknown fig_type %d\n", ftype);
               //exit(0);
            }else{
               new SList(rel_pos,"fig_" + fig_type_map[ftype],&args);
            }
            rel_pos+=sizes32[type]+0x14;
            printbytes(&buf[opos], esz+(pos-opos));
            continue;
        }else if(type==91){ //zeTextDisplay
            esz=0;

            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_pointer(&pos,&b,buf,true));


            uint8_t flen = buf[pos];
            pos++;
            b--;

            for(uint32_t i=0; i < (flen==0x13||flen==0xF?0x13:0xF); i++) //MAX(flen,0xF); i++)
               args.push_back(consume_byte(&pos,&b,buf));

            if(flen != 0x13 && flen != 0xF){
               printf("Taco %x\n", flen);
               extra+=4;
            }

            new SList(rel_pos,"text_display",&args);
            extra+=0xC;
        }else if(type == 92){ //zeInstHeader
            esz=0;
            uint32_t opos=pos;
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf));
            consume_pointer(&pos,&b,buf);


            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            extra=0x20;
            new SList(rel_pos,"inst_header",&args);

            rel_pos+=36+0x20;
            printbytes(&buf[opos], esz+(pos-opos));
            continue;
        }else if(type == 93){ //zeMosaic
            esz=0;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));

            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));

            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            extra=4;
            new SList(rel_pos,"mosaic",&args);
        }else if(type == 94){ //zeAnyInst
            esz=0;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_pointer(&pos,&b,buf,true));
            args.push_back(consume_s32(&pos,&b,buf));
            args.push_back(consume_s32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_s32(&pos,&b,buf));

            uint16_t ftype = __nswap_16(*(uint16_t*)&buf[pos]);
            printf("Ftype: %d %2.2X %2.2X\n", ftype, buf[pos],buf[pos+1]);
            args.push_back(consume_u16(&pos,&b,buf));

            if(ftype){
               args.push_back(consume_byte(&pos,&b,buf));
               args.push_back(consume_byte(&pos,&b,buf));
               extra=4;
            }else{
               extra=8;//0x8
//               esz+=2;
            }
            new SList(rel_pos,"any_inst_" + to_string(ftype),&args);
        }else if(type==95){ //zeMagInst
// 5F 3A 37 80 34 00 00 01 00 10 52 00 00 00
            esz=2;
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_u32(&pos,&b,buf));
            args.push_back(consume_byte(&pos,&b,buf));
            extra+=0;
        }else{
            printf("Unparsed type: 0x%x %d\n", type, type);
            printbytes(&buf[opos], esz+(pos-opos));
            //exit(0);
            assert(false);
        }

        if(frompos.find(rel_pos) == frompos.end()){
            new SList(rel_pos,string("unknown_") + types[type],&args);
        }


        printbytes(&buf[opos], esz+(pos-opos));
        uint32_t asz=esz+(pos-opos)+extra;
        if(asz%4)
          asz+=4-(asz%4);

        if(false){//type==20){//){//type==89){//Fig
           rel_pos += 0x54;
        }else{
           rel_pos += asz-4;
        }
        //printf("rel bump %d\n", asz-4);
        pos+=esz;
        b-=esz;
   }
}


SList* consume_list(SList *l){
   vector<SList*> ret;
   while(l && l->m_atom == "list_node" && l->m_list.size() > 1){
      ret.push_back(consume_list(l->m_list[0]));
      l = l->m_list[1];
   }
   if(!ret.size())
      return l;
   return new SList(0,"",&ret);
}

SList* symbolify(SList* l){
   if(l && l->m_atom.length() && l->m_atom[0] == '\"'){
       return new SList(0,l->m_atom.substr(1,l->m_atom.length()-2),&l->m_list);
   }
   return l;
}

void consume_props(SList *l, bool root=true){
   if(l && l->m_atom == "property") {
      if(l->m_list.size()==2){
          SList *t = l->m_list[0];
          l->m_list[0] = symbolify(l->m_list[1]);
          l->m_list[1] = new SList(0,"->");
          l->m_list.push_back(symbolify(t));
          l->m_atom = "";
      }else if(l->m_list.size()==3){
#if 1
          SList *t = l->m_list[0];
          SList *t2 = l->m_list[1];
          l->m_list[0] = symbolify(l->m_list[2]);
          l->m_list[1] = new SList(0,"->");
          l->m_list[2] = symbolify(t);
          l->m_list.push_back(new SList(0,"="));
          l->m_list.push_back(t2);
          l->m_atom = "";
#endif
      }
      l->m_noparen = !root;
   }
   for(auto it=l->m_list.begin(); it != l->m_list.end(); it++){
      if(*it)
         consume_props(*it,false);
   }
}


void find_node(string a, SList *l, void(*lambda)(SList*) =0){
   if(l && l->m_list.size() && l->m_list[0]->m_atom == a && lambda)
       lambda(l);
   for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          find_node(a,*it,lambda);
}

void find_nodepp(string a, SList *l, void(*lambda)(SList*) =0){
   if(l && l->m_list.size() && l->m_list[0]->m_list.size() && l->m_list[0]->m_list[0]->m_atom == a && lambda)
       lambda(l);
   for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          find_nodepp(a,*it,lambda);
}

void find_nodep(string a, SList *l, void(*lambda)(SList*) =0){
   if(l->m_atom == a && lambda)
       lambda(l);
   for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
       if(*it)
          find_nodep(a,*it,lambda);
}

void swap_back(string a, SList *l){
#if 1
   if(l && l->m_list.size() > 1 && l->m_list[0] && l->m_list[0]->m_atom == a){
      vector<SList*> nl;
      nl.push_back(l->m_list[1]);
      SList* t = l->m_list[0];
      for(auto it=next(l->m_list.begin(),2); it!=l->m_list.end(); it++){
         nl.push_back(t);
         nl.push_back(*it);
      }
      l->m_list = nl;
   }
#endif
   for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++)
      if(*it)
         swap_back(a,*it);
}

void to_parent(string a, SList *l){
   if(l && l->m_list.size() && l->m_list[0]->m_atom == a){
      l->m_atom = l->m_list[0]->m_atom;
      l->m_list.erase(l->m_list.begin());
   }
   for(auto it=l->m_list.begin(); it!=l->m_list.end(); it++){
      if(*it)
        to_parent(a,*it);
   }
}

void proc_fig(SList *root){
   string purpose = root->m_list[1]->m_atom;
   string layer = root->m_list[0]->m_atom;
   root->m_atom = root->m_list[3]->m_atom;
   root->m_list = root->m_list[3]->m_list;

   if(root->m_atom == "bbox"){
       root->m_atom = string("dbCreateRect(nil list(" + purpose + " " + layer + ") list(") +
                      "(" + root->m_list[0]->m_atom + ":" + root->m_list[1]->m_atom + ") " +
                      "(" + root->m_list[2]->m_atom + ":" + root->m_list[3]->m_atom + ")))";
       root->m_escape=false;
       root->m_list.clear();
   }

   if(root->m_atom == "polygon"){
       root->m_atom = string("dbCreatePolygon(nil list(" + purpose + " " + layer + ") list(");
       for(auto it=root->m_list.begin(); it!=root->m_list.end(); it++){
             root->m_atom += "(" + (*it)->m_list[0]->m_atom + ":" + (*it)->m_list[1]->m_atom + ") ";
       }
       root->m_atom += "))";
       root->m_escape=false;
       root->m_list.clear();
   }

   if(root->m_atom == "label"){
       root->m_atom = string("dbCreateLabel(nil list(" + purpose + " " + layer + ") ") +
                      "(" + root->m_list[2]->m_atom + ":" + root->m_list[3]->m_atom + ") " +
                      root->m_list[1]->m_atom + ")";
       root->m_escape=false;
       root->m_list.clear();
   }

   if(root->m_atom == "path"){
       root->m_atom = string("dbCreatePath(nil list(" + purpose + " " + layer + ") list(");
       for(auto it=next(root->m_list.begin(),4); it!=root->m_list.end(); it++){
             root->m_atom += "(" + (*it++)->m_atom + ":";
             root->m_atom += (*it)->m_atom + ") ";
       }
       root->m_atom += "))";
       root->m_escape=false;
       root->m_list.clear();
   }
}

void proc_inst(SList *root){
   SList* hdr = root->m_list[1];
//   root->m_atom = root->m_list[1]->m_atom;
//   root->m_list = root->m_list[1]->m_list;
   if(hdr->m_list.size())
       root->m_atom = string("dbCreateInstByMasterName(nil ") + hdr->m_list[0]->m_atom + " " +
                  hdr->m_list[1]->m_atom + " " + hdr->m_list[2]->m_atom + " " +
                  "\"inst" + root->m_list[5]->m_atom + "\" " +
                  "(" + root->m_list[2]->m_atom + ":" + root->m_list[3]->m_atom + "))";
   root->m_list.clear();
   root->m_escape=false;
}

void proc_skill(SList *root, string prop_name=""){

   rename("symbol","foo",root,[](SList *t) {
       if(!t->m_list.size())
          return;
       string s = t->m_list[0]->m_atom;
       s = s.substr(1,s.length()-2);
       t->m_atom = s;
       t->m_list.clear();
   });

#if 0
   find_node("let", root, [](SList *t) {
       t->m_list[1]->m_list[0]->m_list = consume_list(t->m_list[1]->m_list[0]);
   });

   find_node("procedure", root, [](SList *t) {
       t->m_list[1]->m_list[0]->m_list = consume_list(t->m_list[1]->m_list[0]);
   });

   find_node("dbReplaceProp", root, [](SList *t) {
       t->m_list[1]->m_list = consume_list(t->m_list[1]);
   });

   find_node("dbCreateRect", root, [](SList *t) {
       t->m_list[1]->m_list = consume_list(t->m_list[1]);
   });
#endif
   find_nodep("list_node", root, [](SList *t) {
       t->m_list = consume_list(t)->m_list;
       t->m_atom = "";
   });

   rename("setq","=",root);
   rename("getSGq","~>",root);
   rename("plus","+",root);
   //rename("minus","-",root);
   rename("equal","==",root);
   rename("greaterp",">",root);
   rename("nequal","!=",root);
   rename("difference","-",root);
   rename("quotient","/",root);
   rename("times","*",root);
   rename("lessp","<", root);
   rename("and","&&", root);
   rename("or","||", root);
   rename("range",":", root);
   rename("quote","'", root);
   rename("null","!", root);


   swap_back("=",root);
   swap_back("~>",root);
   swap_back("+",root);
   //swap_back("-",root);
   swap_back("==",root);
   swap_back(">",root);
   swap_back("!=",root);
   swap_back("-",root);
   swap_back("/",root);
   swap_back("*",root);
   swap_back("<",root);
   swap_back("&&",root);
   swap_back("||",root);
   swap_back(":",root);

   to_parent("if",root);
   to_parent("when",root);
   to_parent("while",root);
   to_parent("foreach",root);
   to_parent("unless",root);
   to_parent("return",root);

//   rename("while","if", root);

#if 1
   find_node("procedure", root, [](SList *t) {
       SList* name = t->m_list[1]->m_list[0];
       SList* args = new SList(0,"",&t->m_list[1]->m_list);
       args->m_list.erase(args->m_list.begin());
       t->m_list[1]->m_list.resize(1);
       t->m_list[1]->m_list.push_back(args);
       t->m_list[1]->m_list.push_back(t->m_list[2]);
       t->m_list.resize(2);
   });
#endif

   find_node("let", root, [](SList *t) {
       t->m_list[0]->m_list.push_back(t->m_list[1]);
       for(auto it=next(t->m_list.begin(),2); it!=t->m_list.end(); it++){
          t->m_list[0]->m_list.push_back(*it);
       }
       t->m_list.resize(1);
       t->m_atom = t->m_list[0]->m_atom;
       t->m_list = t->m_list[0]->m_list;
   });

#if 0
  find_nodep("group_member", root, [](SList *t) {
       printf("ugh\n");
       exit(0);
       t->m_list.clear();
   });
#endif

  find_node("exists", root, [](SList *t) {
       t->m_atom = t->m_list[0]->m_atom;
       t->m_list.erase(t->m_list.begin());
   });

  find_node("for", root, [](SList *t) {
       t->m_atom = t->m_list[0]->m_atom;
       t->m_list.erase(t->m_list.begin());
   });

   find_node("prog", root, [](SList *t) {
       t->m_list[0]->m_list.push_back(t->m_list[1]);
       for(auto it=next(t->m_list.begin(),2); it!=t->m_list.end(); it++){
          t->m_list[0]->m_list.push_back(*it);
       }
       t->m_list.resize(1);
   });

   find_node("setSGq", root, [](SList *t) {
       t->m_list.resize(5);
       t->m_list[0] = t->m_list[1];
       t->m_list[1] = new SList(0,"~>");

       t->m_list[4] = t->m_list[2];
       t->m_list[2] = t->m_list[3];
       t->m_list[3] = new SList(0,"=");

   });

#if 1
   find_node("list", root, [](SList *t) {
       t->m_atom = "list";
       t->m_list.erase(t->m_list.begin());
   });
#endif

//   root->m_noparen=true;
//   root->m_list[0]->m_noparen=true;

   set<SList*> parents;
   FILE *f=0;
   if(prop_name == "\"procedure\""){
      f = fopen("out.il","w");
      if(root->m_list.size())
         root = root->m_list[0]; //TODO: not sure if this will always work
      root->m_noparen=true;
   }
   print_reset(f);
   parents.clear();
   root->print(&parents);
   printf("\n");
   if(f)
      fclose(f);
}

string get_cell_name(char* fname) {
  char *pch = strtok (fname,"/\\");
  vector<string> tokens;
  while(pch){
    tokens.push_back(pch);
    pch = strtok (NULL, "/\\");
  }
  return tokens[tokens.size()-3];
}

int main(int argc, char** argv){
   //Load entire file into memory
   //FILE* f = fopen("LAYOUT.CDB","r");
   if (argc > 3) {
     fprintf(stderr, "Too many arguments: command <file> [<num>]\n");
     return -1;
   }
   if (argc < 2) {
     fprintf(stderr, "Not enough arguments: command <file> [<num>]\n");
     return -1;
   }
   if( access( argv[1], F_OK ) == -1 ) {
     fprintf(stderr, "No such file: %s (want a layout.cdb file)\n", argv[1]);
     return -1;
   }

   FILE* f = fopen(argv[1],"r");

   fseek(f,0,SEEK_END);
   size_t sz = ftell(f);
   fseek(f,0,SEEK_SET);
   uint8_t *buf = (uint8_t*)valloc(sz);
   fread(buf,sz,1,f);
   fclose(f);
   uint32_t srcid = *(uint32_t*)&buf[0x0];
   uint32_t maybe_len = *(uint32_t*)&buf[0x4];
   char* date = (char*)&buf[8];
   uint32_t nsegs = *(uint32_t*)&buf[0x20];
   uint32_t endian = *(uint32_t*)&buf[0x2C];
   char* text0 = (char*)&buf[0x30];


   endian = __bswap_32(endian);
   big_endian = endian == 0x1020304;

   maybe_len = __nswap_32(maybe_len);
   nsegs = __nswap_32(nsegs);


   printf("SrcID: %X, Date: %s, Data Len: %d, Segments %X, Endian: %X, Txt: %s @%s\n", srcid, date, maybe_len, nsegs, endian, text0, argv[1]);

   uint64_t pos=0x80;
   for(uint32_t i=0; i < nsegs; i++){
       uint64_t seg_start=pos;
       //Seg is 0x40 bytes
       uint32_t e = __nswap_32(*(uint32_t*)&buf[pos+0x4]); //Checksum

       uint32_t a = __nswap_32(*(uint32_t*)&buf[pos+0xc]);
       uint32_t b = __nswap_32(*(uint32_t*)&buf[pos+0x10]);
       uint32_t c = __nswap_32(*(uint32_t*)&buf[pos+0x14]);
       uint32_t d = __nswap_32(*(uint32_t*)&buf[pos+0x18]);


       uint32_t compress = buf[pos+0x20];
       //if(0x20&1) compressed
       printf("Segment %x L:%x %x %x %lx %x %x, DCL: %x\n", a, b, c, d, pos, e, compress, d-0x18);

//       printbytes(&buf[pos], 0x50);

       printbytes(&buf[pos+0x0], 0x40);

       //Segment checksum
       uint32_t sum=0;
       for(uint32_t i=0; i < b; i++){
          sum = (((int8_t*)buf)[pos+i]) + ((int)sum)*3;
       }
       printf("Sum: %x\n", sum);

       pos+=0x40;
if(argc<3 || i==atoi(argv[2])){
       if((compress&1)==0){
          parseseg(buf,seg_start,pos,i, b);
       }else
          parsecseg(buf,seg_start,pos,i, b, argv[1]);
}
       pos+=b;
}
   //    assert((d-0x18) % esz == 0);
#endif

   printf("%lx %lx\n", pos, sz);

   uint32_t dangles=0;
   vector<SList*> allobjs;
   vector<uint32_t> tgts, refs;
   for(auto it=frompos.begin(); it!=frompos.end(); it++){
      //printf("%X\n", (*it).first);
      if((*it).first){
        allobjs.push_back((*it).second);
        tgts.push_back((*it).second->m_ofst);
      }
   }

   //exit(0);
   for(auto it=allobjs.begin(); it!=allobjs.end(); it++){
      if((*it)->m_tgt)
         continue;
      for(auto it2=(*it)->m_list.begin(); it2!=(*it)->m_list.end(); it2++){
         if(!(*it2)->m_tgt)
           continue;
         uint32_t tgt=(*it2)->m_tgt;
         refs.push_back(tgt);
         SList* stgt = (*frompos.find(tgt)).second;
         if(!stgt){
           dangles++;
           continue;
         }
         *it2=stgt;
         consumed.insert(stgt->m_ofst);
      }
   }

#if 1
   sort(tgts.begin(), tgts.end());
   sort(refs.begin(), refs.end());
   printf("Tgts:\n");
   uint32_t last=0;
   uint32_t base=0x10000;
   uint32_t len=0x50000;
   for(auto it=tgts.begin(); it!=tgts.end(); it++)
      if(*it>=base && *it<base+len && *it != last){
         printf("%X %X\n", *it, *it - last);
         last=*it;
      }
   printf("Refs:\n");
   last=0;
   for(auto it=refs.begin(); it!=refs.end(); it++)
      if(*it>=base && *it<base + len && *it != last){
         printf("%X %X\n", *it, *it - last);
         last=*it;
      }
#endif

#if 1
   vector<SList *> properties,groups,lps;
   for(auto it=allobjs.begin(); it!=allobjs.end(); it++){
      //if(!(*it)->m_list.size())
      //   continue;
      //if(consumed.find((*it)->m_ofst) != consumed.end())
      //   continue;
      if((*it)->m_atom == "property"){
         properties.push_back(*it);
         consumed.insert((*it)->m_ofst);
      }
      if((*it)->m_atom == "group"){
         groups.push_back(*it);
         consumed.insert((*it)->m_ofst);
      }
      if((*it)->m_atom == "LP"){
         lps.push_back(*it);
         consumed.insert((*it)->m_ofst);
      }
   }

#if 1
   for(auto it=properties.begin(); it!=properties.end(); it++){
      //Property type only yields result type. Could be function/constant/ptr
      if((*it)->m_list.size() < 4){ //Came from PROP.XX
          consume_props(*it);
          proc_skill(*it);
          //set<SList*> parents;
          //(*it)->print(&parents);
          //printf("\n");
          continue;
      }
      int type = atoi((*it)->m_list[1]->m_atom.substr(5,1).c_str());
      string rtype = prop_types[type];
      printf("property %s %s %s %d\n", (*it)->m_list[0]->m_atom.c_str(), (*it)->m_list[2]->m_atom.c_str(), rtype.c_str(), type );
      if(type == 4 || type == 0xd){
          proc_skill((*it)->m_list[3],(*it)->m_list[0]->m_atom);
      }

      if(type == 0 || type == 1 || type == 2 || type == 3){
         set<SList*> parents;
         print_reset(0);
         parents.clear();
         (*it)->m_list[3]-> print(&parents);
         printf("\n");
      }
      if((*it)->m_list.size() > 4){
         set<SList*> parents;
         print_reset(0);
         parents.clear();
         (*it)->m_list[4]-> print(&parents);
         printf("\n");
      }
   }
#endif
   printf("groups begin\n");
   for(auto it=groups.begin(); it!=groups.end(); it++){
//       proc_skill(*it);
         set<SList*> parents;
         print_reset(0);
         parents.clear();
         (*it)->print(&parents);
         printf("\n");
   }

   printf("\ndang done %s\n", argv[1]);

   printf("lps begin\n");
   for(auto it=lps.begin(); it!=lps.end(); it++){
//       proc_skill(*it);
         set<SList*> parents;
         print_reset(0);
         parents.clear();
         (*it)->print(&parents);
         printf("\n");
   }

   printf("\ndang done %s\n", argv[1]);

   vector<SList*> statics;
   for(auto it=allobjs.begin(); it!=allobjs.end(); it++){
      if(!(*it)->m_list.size())
         continue;
      if(consumed.find((*it)->m_ofst) != consumed.end())
         continue;

       if((*it)->m_atom.rfind("fig_",0)==0){
          proc_fig(*it);
          statics.push_back(*it);
       }else if((*it)->m_atom.rfind("any_inst_",0)==0){
          proc_inst(*it);
          statics.push_back(*it);
       }
   }

   string cell_name = get_cell_name(argv[1]);
   string str = string("procedure  (pcGenCell_") + cell_name + "  (pcCellView \"d\")";
   statics.push_back(new SList(0,")"));
   SList *prog=new SList(0,str,&statics);
   prog->m_escape=false;
   {
       set<SList*> parents;
       string ofile = ("output/" + cell_name + ".il");
       FILE *f = fopen(ofile.c_str(),"w+");
       if (f == NULL) {
         int errnum = errno;
         fprintf(stderr, "Unable to create output file '%s': %s\n", ofile.c_str(), strerror( errnum ));
         return -1;
       }
exit(0);
       print_reset(f);
       parents.clear();
       prog->print(&parents);
       printf("\n");
       fclose(f);
   }

#endif

#if 0
   printf("%ld\n", sizeof(types)/sizeof(char*));

   for(int i=0; i < 97; i++){
      if(!stringidx[i])
         continue;
      printf("%16.16s\t%2d\t%3d\n", types[i],i,sizes32[i]);
   }
#endif
}
