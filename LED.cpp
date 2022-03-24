// ConsoleApplication1.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <iostream>
#include <cstdlib>
#include <string>
#include <windows.h>
#include <vector>



using namespace std;

// 所有字体形式
vector<string> fonts = { "hzk16s","hzk16f","hzk16h","hzk16k","hzk16l" };
// 所有动画效果
vector<string> animations = { "水平滚动","垂直滚动" };
// 字体形式的个数
const int font_num = 5;
// 汉字的最多输入个数
const int hanzimax_num = 8;
// 每个字所占一行的点数
const int hanzi_size = 16;
// 每行输出汉字所占的点数
const int N = hanzi_size * hanzimax_num;
//一个汉字所占比特数
const int hanzi_bit = hanzi_size * hanzi_size / 8;
// 汉字输出区域
int area[hanzi_size][N];
//定义空文件
FILE* fphzk = NULL;
// 汉字的字数
size_t hanzi_zishu = 0;

// 取模 
int mod(int x, int y)
{
	return (x % y + y) % y;
}

// 设置显示的颜色
// x: 1 蓝色 2 深绿色 3浅蓝色 4 红色 5 深紫色 6 土黄色... 15 亮白色
void set_font_color(int x) {
	HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
	SetConsoleTextAttribute(h, x);
}

// 建立坐标系，确定汉字的位置
void zuobiaoxi(int x, int y)
{
	COORD pos;
	pos.X = x;
	pos.Y = y;
	SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), pos);
}

//建立菜单
int menu() 
{
	int font_Selected;
	system("cls");
	cout << "\n\
    |================欢迎进入滚动字幕系统=============|\n\
    |                      0.退出程序                 |\n\
    |======================字体种类===================|\n\
    |                      1.宋体                     |\n\
    |                      2.仿宋体                   |\n\
    |                      3.黑体                     |\n\
    |                      4.楷体                     |\n\
    |                      5.隶书                     |\n\
    |======================动画效果===================|\n\
    |                      1.水平滚动                 |\n\
    |                      2.垂直滚动                 |\n\
    |                      3.水平卷轴                 |\n\
    |                      4.下雪特效                 |\n\
    |=================================================|\n\n";
	printf("请选择字体选项(请输入1~5）：\n");
	scanf_s("%d", &font_Selected);
	return font_Selected;
}

//水平滚动效果
void horizontal_move() 
{
	for (int t = 0; ; t = (t + 1) % N) {
		system("cls");
		for (int i = 0; i < hanzi_size; i++) {
			for (int j = 0; j < N; j++) {
				if (area[i][mod(j - t, N)]) {
					zuobiaoxi(j, i);
					cout << '*';
				}
			}
		}
		Sleep(100);
	}
}
//垂直滚动效果
void vertical_move() 
{
	for (int t = 0; ; t = (t + 1) % N) {
		system("cls");
		for (int i = 0; i < hanzi_size; i++) {
			for (int j = 0; j < N; j++) {
				if (area[mod(i + t, hanzi_size)][j]) {
					zuobiaoxi(j, i);
					cout << '*';
				}
			}
		}
		Sleep(100);
	}
}

// 显示效果
void stdout_display(int array[hanzi_size][N]) {
	for (int i = 0; i < hanzi_size; i++) {
		for (int j = 0; j <	N; j++) {
			if (array[i][j]) {
				zuobiaoxi(j, i);
				cout << '*';
			}
		}
	}
}


void scroll() {
	int frame_number = hanzi_zishu / 2.0 * 16;
	while (1) {
		int effect[hanzi_size][N] = { 0 };
		for (int i = 0; i < frame_number + 1; i++) {
			system("cls");
			if (i != 0) {
				// 复制area两列到effect
				for (int k = 0; k < 16; k++) {
					effect[k][N / 2 - i] = area[k][frame_number - i];
					effect[k][N / 2 + i - 1] = area[k][frame_number + i - 1];
				}
			}
			// 两列外侧加上画轴
			if (i != frame_number) {
				for (int k = 0; k < 16; k++) {
					effect[k][N / 2 - i - 1] = 1;
					effect[k][N / 2 + i] = 1;
				}
			}
			// 显示
			stdout_display(effect);
			Sleep(100);
		}
		Sleep(1000);

		for (int i = frame_number + 1; i >= 0; i--) {
			system("cls");
			// 消失的过程，将画轴往中间移动
			if (i != frame_number + 1) {
				for (int k = 0; k < 16; k++) {
					effect[k][N / 2 - i - 1] = 0;
					effect[k][N / 2 + i] = 0;
					if (i != 0) {
						effect[k][N / 2 - i] = 1;
						effect[k][N / 2 + i - 1] = 1;
					}
				}
			}
			// 显示
			stdout_display(effect);
			Sleep(100);
		}
		Sleep(1000);
	}
}


void snow() {
	// 把原本的area数组相邻两行增加一行空间下落并堆叠
	int** temp = new int* [31];
	for (int i = 0; i < 31; i++)
	{
		temp[i] = new int[N];
		for (int j = 0; j < N; j++) {
			temp[i][j] = 0;
		}
	}

	int start_col = 64 - hanzi_zishu * 8;
	for (int i = 0; i < 31; i++) {
		if (i % 2 == 0) {
			for (int k = 0; k < hanzi_zishu * 16; k++) {
				temp[i][start_col + k] = area[hanzi_size - 1 - i / 2][k];
			}
		}
	}

	while (1) {
		int effect[hanzi_size][N] = { 0 };
		// 落下过程一共31帧
		for (int i = 0; i < 31; i++) {
			system("cls");
			// 没有一行落地，都在空中
			if (i < 16) {
				for (int j = 0; j <= i; j++) {
					for (int k = 0; k < N; k++) {
						effect[i - j][k] = temp[j][k];
					}
				}
			}
			//至少有一行落地
			else {
				for (int j = 0; j < hanzi_size; j++) {
					for (int k = 0; k < N; k++) {
						effect[j][k] = temp[i-j][k];
					}
				}
				for (int j = 15; j >= 30 - i; j--) {
					for (int k = 0; k < hanzi_zishu * 16; k++) {
						effect[j][start_col + k] = area[j][k];
					}
				}
			}
			stdout_display(effect);
			Sleep(100);
		}
		Sleep(1000);
	}
	for (int i=0;i<31;i++){
		delete[] temp[i];
	}
}


//选择字体
void chose_font(int font_Selected)
{
	switch (font_Selected)
	{
	case 0:
		exit(0);
		printf("即将退出程序！");
		break;
	case 1:
		fphzk = fopen("hzk16s","rb");
		break;
	case 2:
		fphzk = fopen("hzk16f", "rb");
		break;
	case 3:
		fphzk = fopen("hzk16h", "rb");
		break;
	case 4:
		fphzk = fopen("hzk16k", "rb");
		break;
	case 5:
		fphzk = fopen("hzk16l", "rb");
		break;
	default:
		printf("输入错误！");
		break;
	}
}
//选择动画效果
void chose_animation(int animation_Selected)
{
	switch (animation_Selected)
	{
	case 0:
		exit(0);
		printf("即将退出程序！");
		break;
	case 1:
		horizontal_move();
		break;
	case 2:
		vertical_move();
		break;
	case 3:
		scroll();
	case 4:
		snow();
	default:
		printf("输入错误！");
		break;
	}
}
//输入汉字并存入缓存区
void create_board(FILE* f)
{
	int offset;
	string content;
	cin >> content;
	// 对超出最大字数的汉字进行删除
	if (content.size() > hanzimax_num * 2)
	{
		content = content.substr(0, hanzimax_num * 2);
	}
	
	unsigned char buffer[32];
	char* hanzi = (char*)content.c_str();
	hanzi_zishu = content.size()/2;
	for (int num = 0; *hanzi; hanzi += 2, num++) 
	{
		unsigned char high = *hanzi - 0xa1;
		unsigned char low = *(hanzi + 1) - 0xa1;
		// 在字体文件中读取改字对应的点阵信息
		offset = (94 * high + low) * hanzi_bit;
		fseek(f, offset, SEEK_SET);
		fread(buffer, sizeof(unsigned char), hanzi_bit, f);
		for (int i = 0; i < hanzi_size; i++) 
		{
			for (int j = 0; j < hanzi_size / 8; j++) 
			{
				int buffer0 = buffer[i << 1 | j];
				for (int k = 0; k < 8; k++)
				{
					area[i][num * 16 + j * 8 + k] = (buffer0 & 0x80) ? 1 : 0;
					buffer0 <<= 1;
				}
			}
		}
	}
}

int main()
{
	while (1)
	{
		int animation_Selected;
		int choice = menu();
		chose_font(choice);
		printf("请选择动画效果(请输入1~4）：\n");
		scanf_s("%d", &animation_Selected);
		printf("请输入您要显示的汉字（八个汉字以内）：\n");
		create_board(fphzk);
		set_font_color(3);
		chose_animation(animation_Selected);
		fclose(fphzk);
	}
	return 0;
}
