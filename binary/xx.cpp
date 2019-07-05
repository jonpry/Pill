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

const char *types[] = { "0", "char", "short", "69", "long", "float", "double", "pointer",
                         "byte", "43", "43", "LPType", "4D", "MXR90", "4D", "MYR90", 
                         "50", "XXString", "XXfreeObject", "XXfreeObject2", "XXgroup",
                         "XXgroupMember", "XXilList", "XXilSymbol", "XXparentChild",
                         "XXpropVal", "XXpropery", "XXrange", "58", "aBoolean",
                         "aDouble", "aFileName", "aFloat", "aIlExpr", "61", "aNetSet",
                         "aNlpExpr", "aProperty", "aRange", "aSelfIdent", "aString",
                         "aTime", "accessDir", "ailList", "analog", "61", "arcType",
                         "ascOwnrType", "assocOwner", "assocOwnerUnion", "assocType",
                         "assocUnion", "associate", "attrAssocType", "attrOwner",
                         "bBox", "62", "beginExt", "behavioral", "bytes", "cellName",
                         "cellViewType", "child", "clock", "columnBiasedMos",
                         "columnOffset", "columnSpacing", "columns", "connStatus",
                         "connectOutside", "connected", "contraints", "criticality",
                         "dataFileId", "dbBBox", "dbPoint", "defValue", "delta", 
                         "deltaX", "deltaY", "deltas", "direction", "displayFlags",
                         "donut", "donutType", "dot", "dotType", "dummy1", "dummy2",
                         "dummy3", "dummyType1", "dummyType2", "dummyType3", 
                         "dummyType4", "dummyType5", "dummyType6", "dummyType7",
                         "edgeConnected", "ellipse", "ellipseType", "emptyMosaic",
                         "endExt", "extendExtend", "fig", "66", "flags", "freeArraySize",
                         "graphic", "ground", "group", "groupMemType", "groupType",
                         "headerRef", "height", "68", "icon", "index", "input", 
                         "inputOutput", "inst", "instHeader", "instHeaderType",
                         "instInfo", "instPin", "instPinType", "instPinUnion", 
                         "instTerm", "instTermType", "instTermUnion", "instType",
                         "instanceList", "instances", "instsBBox", "isGlobal", 
                         "isStart1", "isStart2", "jumper", "lBound", "label",
                         "labelAssocType", "labelType", "largeNetNumBits",
                         "largeSigArray", "lastInGroup", "lastSigArySize", "layer",
                         "libName", "line", "lineType", "locked", "logicModel",
                         "lowerLeft", "6D", "magInst", "magInstInfo", "manh2line",
                         "manh2path", "maskLayout", "masterAttr", "masterBBox",
                         "masterMemRcb", "masterProp", "masterTermAttr", "masterTermProp",
                         "maxExtension", "memNet", "members", "memoryRcb", 
                         "modifiedButNotSaved", "mosaic", "mosaicInstType",
                         "mosaicTileType", "mosaicType", "nPoints", "nShapes",
                         "name", "nameNumber", "nameString", "needToConnect",
                         "net", "netFig", "netType", "netUnion", "netlist", 
                         "next", "nextFree", "nextGroup", "nextGroupForObject",
                         "nextInAssoc", "nextInGroup", "nextInObj1", "nextInObj2",
                         "nextInOwner", "nextInView", "nextOnInst", "nextOnInstTerm",
                         "nextOnNet", "nextOnTerm", "numBits", "numInst", "numInstTypes",
                         "numInstances", "numMemNet", "6F", "6F", "object", "offset",
                         "ofjbtd", "oldInst", "orient", "output", "owner", 
                         "package", "70", "padSpace1", "padSpace2", "padSpace3",
                         "padSpace4", "pair", "paramAssocType", "parent", "path",
                         "pathType", "personality", "pin", "pinType", "pinUnion",
                         "placeInfo", "placeStatus", "placed", "point0", "points",
                         "polygon", "polygonType", "prefixChar", "70", "propAssocType",
                         "propType", "purpose", "quad", "r0", "72", "72", "72", "72",
                         "readInFlag", "rect", "rectType", "regularMosaic", "roundRound",
                         "rowBiasedMosaic", "rowOffset", "rowSpacing", "rows", 
                         "sBounds", "schematic", "schematicSymbol", "shape",
                         "sibling", "sigArray", "sigType", "signal", "simpleMosaic",
                         "startAngle", "stranger", "style", "subInfo", "subInst",
                         "suggested", "supply", "sweepAngle", "switch", 
                         "symbolic", "term", "termType", "termUnion", "testLatch",
                         "text", "textDisplay", "textDisplayType", "theLabel", 
                         "timeStamp", "truncateExtend", "type", "uBound", 
                         "75", "75", "uint1D", "unknown", "unplaced", "unused",
                         "unused2", "unused3", "upperRight", "usedIn", "value",
                         "valueType", "varExtendExtend", "variants", "verilogMap",
                         "view", "viewName", "76", "voftjdP", "width", "78",
                         "xy", "y", "yFirst", "ze2OldMosaic", "zeAnyInst", 
                         "zeAnyInstName", "zeArc", "zeCellView", "zeDonut",
                         "zeFigPar", "zeInst", "zeInstHeader", "zeInstInfo",
                         "zeInstName", "zeInstPin", "zeInstTerm", "7A", 
                         "zeLabel", "zeLine", "zeLrgSigAryInfo", "zeMagInst",
                         "zeMagInstInfo", "zeMosaic", "zeMosaicTile", "zeNet",
                         "zeNetFigUnion", "zeOldFig", "zeOldInstHeader", "zeOldMosaic",
                         "zeOldNetFig", "zeOldTextDisplay", "zeOrthPolygon",
                         "zePath", "zePhysConn", "zePin", "zePinFigUnion", 
                         "zePlacementInfo", "zePolygon", "zeSig", "zeTerm", 
                         "zeTextDisplay", "7A", "zeUX2", "7A", "zeUY2", 
                         "zeUnionX", "zeUnionY", "zebBox", "zeoldFigPar", 
                         "zeoldsubInfo", "zeoldsubInst", "zesubinfo", "zesubInst"}; 

int main(){
   //Load entire file into memory
   FILE* f = fopen("LAYOUT.CDB","r");
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
   maybe_len = __bswap_32(maybe_len);
   nsegs = __bswap_32(nsegs);
 
   printf("SrcID: %X, Date: %s, Data Len: %d, Segments %X, Endian: %X, Txt: %s\n", srcid, date, maybe_len, nsegs, endian, text0);

   uint64_t pos=0x80;
   for(uint32_t i=0; i < nsegs; i++){
       //Seg is 0x40 bytes
       uint32_t e = __bswap_32(*(uint32_t*)&buf[pos+0x4]); //Checksum

       uint32_t a = __bswap_32(*(uint32_t*)&buf[pos+0xc]);
       uint32_t b = __bswap_32(*(uint32_t*)&buf[pos+0x10]);
       uint32_t c = __bswap_32(*(uint32_t*)&buf[pos+0x14]);
       uint32_t d = __bswap_32(*(uint32_t*)&buf[pos+0x18]);


       uint32_t compress = buf[pos+0x20];
       //if(0x20&1) compressed
       printf("Segment %x %x %x %x %lx %x %x, DCL: %x\n", a, b, c, d, pos, e, compress, d-0x18);

       uint32_t type = buf[pos+0x40];
       uint32_t ea = __bswap_16(*(uint16_t*)&buf[pos+0x41]);
       uint32_t esz = __bswap_16(*(uint16_t*)&buf[pos+0x52]);

for(int j=0x18; j < 0x19; j++){
       uint32_t eb = __bswap_16(*(uint16_t*)&buf[pos+0x4e +j]);
       uint32_t ec = __bswap_16(*(uint16_t*)&buf[pos+0x58+j]);
       uint32_t ed = __bswap_16(*(uint16_t*)&buf[pos+0x68+j]);

       printf("El %x %x %x %x %x %x\n", type, ea, esz, eb, ec, ed);
}
       uint32_t sum=0;
       for(uint32_t i=0; i < b; i++){
          sum = (((int8_t*)buf)[pos+0x40+i]) + ((int)sum)*3;
       }
       printf("Sum: %x\n", sum);
       pos+=0x40+b;
   }
}
