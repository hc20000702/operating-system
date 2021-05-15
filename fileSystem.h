#include <iostream>
#include <stdio.h>
#include <fstream>
#include <string.h>

#include "define.h"
#include "dataStruct.h"

using namespace std;

char buf[TOTAL_SIZE];
// 模拟磁盘
// #0: 不用  #1: 超级块  #2~124: 文件目录表
// #125: inode位图 #126~127: 数据块位图
// #128~283: inode数据 #284~16383: 数据块
FILE* virtualDisk;
// 超级块
struct SuperBlock* superBlock;


// 初始化+格式化磁盘, 只执行一次
int initialize(const char* path)
{
    virtualDisk = fopen(path, "wb+");
    memset(buf, 0, sizeof(buf));
    fwrite(buf, 1, TOTAL_SIZE, virtualDisk);
    if (virtualDisk == NULL)
    {
        return ERROR_VM_NOEXIST;
    }
    // 格式化
    // 写入superBlock
    superBlock = (struct SuperBlock*)calloc(1, sizeof(struct SuperBlock));
    fseek(virtualDisk, START, SEEK_SET);    // 找到盘块#1
    superBlock->size = 16*1024*1024;
    fwrite(superBlock, sizeof(struct SuperBlock), 1, virtualDisk);
    fflush(virtualDisk);

    fclose(virtualDisk);
    return NO_ERROR;
}

// 加载磁盘
int loadVirtualDisk(const char* path)
{
    
}

