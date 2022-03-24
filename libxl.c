#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include "libxl.h" // 本程序使用LibXL库来处理.xls文件，但是免费版一次只能读取300次数据，并且不能写入第一行
// 程序中注释掉的部分只能在购买库后使用，为了克服这个问题，我们每次读取一列就新建一个book变量

// 从sheet1中拷贝col数组代表的列到sheet2, size代表行数
int copySheet(SheetHandle sheet1, SheetHandle sheet2, int* col, int size)
{
	for (int j = 0; j < size; j++) {
		for (int i = 0; i<xlSheetLastRow(sheet1); i++) {
			const wchar_t* tmp = xlSheetReadStr(sheet1, i, col[j], 0);
			//printf("%ls", tmp);
			xlSheetWriteStr(sheet2, i, col[j], tmp, 0);
		}
	}
}
// 实现python等语言的range函数
int* range(int start, int stop, int step) {
	int n = (stop - start - 1) / step + 1;
	int* const a = (int*)malloc(sizeof(int)*n);
	for (int i = 0; i < n; i++) {
		a[i] = start + i * step;
		//printf("%d\t", a[i]);
	}
	return a;
}
// 从sheet中求col_list数组代表的列索引的总和并按行赋值给data数组,size代表行数
//void extradata(SheetHandle sheet, int* col_list, int colsize, double *data, int size) {
//	for (int i = 1; i <= size; i++) {
//		double sum = 0.0;
//		for (int j = 0; j < colsize; j++)
//			sum += _wtof(xlSheetReadStr(sheet, i, col_list[j], 0));
//		data[i-1] = sum;
//	}
//}


// 从文件的sheet)index个sheet中求col_list数组代表的列索引的总和并按行赋值给data数组,size代表行数
void extradata(int sheet_index, int* col_list, int colsize, double* data, int size) {
	// 每读取一列，使用一个新的book变量
	BookHandle* book = (BookHandle*)malloc(sizeof(BookHandle) * colsize);
	wchar_t* file_name = L"D:\\178_75.xls"; // 要读取的文件的位置
	for (int i = 0; i < colsize; i++) {
		book[i] = xlCreateBook();
		xlBookLoad(book[i], file_name);
	}
	for (int i = 1; i <= size; i++) {
		double sum = 0.0;
		for (int j = 0; j < colsize; j++) {
			sum += _wtof(xlSheetReadStr(xlBookGetSheet(book[j], sheet_index), i, col_list[j], 0));
		}
		data[i - 1] = sum;
	}
	for (int i = 0; i < colsize; i++) xlBookRelease(book[i]);
}

//往sheet的第col列按行写入data数组的各个元素，size代表行数
void write_col_data(SheetHandle sheet, int col, double* data, int size) {
	for (int i = 1; i <= size; i++) {
		xlSheetWriteNum(sheet, i, col, data[i-1], 0);
	}
}
// 将提取求和和写入新的sheet结合在一起
//void extra_write(SheetHandle sheet1, SheetHandle sheet2, int* col_list, int colsize, double* data, int size, int col) {
//	extradata(sheet1, col_list, colsize, data, size);
//	write_col_data(sheet2, col, data, size);
//}

// 将提取求和和写入新的sheet结合在一起
void extra_write(SheetHandle sheet, int sheet_index, int* col_list, int colsize, double* data, int size, int col) {
	extradata(sheet_index, col_list, colsize, data, size);
	write_col_data(sheet, col, data, size);
}
// 计算等长度数组sum和data的和并储存在sum中，size代表数组的长度
void sum(double* sum, double* data, int size) {
	for (int i = 0; i < size; i++) {
		sum[i] += data[i];
	}
}
// 分数段统计，data是百分制成绩，interval是各分数段人数，size是总人数，best用来储存成绩较高的人的成绩，index用来记录这些人的索引
void statistics(double* data, int* interval, int size, double* best,int* index) {
	int j = 0;
	for (int i = 0; i < size; i++) {
		if (data[i] < 60) interval[0]++;
		else if (data[i] < 70) interval[1]++;
		else if (data[i] < 80) interval[2]++;
		else if (data[i] < 90) {
			interval[3]++;
			best[j] = data[i];
			index[j++] = i;
		}
		else { 
			interval[4]++;
			best[j] = data[i];
			index[j++] = i;
		}
	}
}
// 打印出sheet中某行的所有元素
void print_best(SheetHandle sheet, int row, int colwidth) {
	printf("Excellent Students:\n");
	printf("Index %d:", row);
	for (int i = 0; i < colwidth; i++) {
		if ((i == 0) | (i == 1))
			printf("%ls\t", xlSheetReadStr(sheet, row, i, 0));
		else
			printf("%f\t", xlSheetReadNum(sheet, row, i, 0));
	}
	printf("\n");
}
// 打印分数段信息
void print_interval(int* interval) {
	printf("分数段：\t人数：\n");
	char a[5][10] = { "[0, 60)","[60, 70)" ,"[70, 80)" ,"[80, 90)" ,"[90, 100)" };
	for (int i = 0; i < 5; i++)
		printf("%s%12d\n", a[i], interval[i]);
}

void name_col(SheetHandle sheet) {
	xlSheetInsertRow(sheet, 1, 1);
	wchar_t col_names[10][12] = { L"学号", L"姓名", L"单选题", L"选择题", L"填空题", L"判断题", L"编程题", L"总成绩", L"百分制成绩", L"修订成绩" };
	for (int i = 0; i < 10; i++) {
		xlSheetWriteStr(sheet, 1, i, col_names[i], 0);
	}
}

int main()
{	
	setlocale(LC_ALL, ""); // 用来打印中文
	BookHandle book = xlCreateBook(); // 用来打开成绩文件
	BookHandle tbook = xlCreateBook(); // 创建一个新的.xls文件
	//xlBookSetLocale(book, L"utf-8");
	//xlBookSetLocale(tbook, L"utf-8");
	SheetHandle tsheet = xlBookAddSheet(tbook, L"Sheet1", 0); // 在新的workbook中创建一个worksheet 
	int col[] = { 0,1 }; // 复制sheet的列索引
	if (xlBookLoad(book, L"D:\\178_75.xls")) copySheet(xlBookGetSheet(book, 1), tsheet, col, 2); // 在新文件中写入学号和姓名
	xlBookRelease(book);
	const int* data_col_range = range(2, 201, 4); // 文件中出现成绩的列的索引
	double data[126]; // 储存各题的总成绩
	double sum_data[126] = { 0.0 }; // 储存总成绩
	extradata(1, data_col_range, 3, data, 126);
	//选择题成绩
	extra_write(tsheet, 1, data_col_range, 3, data, 126, 2); // 提取文件中第1题的成绩总成绩并存入新的sheet中
	sum(sum_data, data, 126); // 计算前1题的总成绩
	extra_write(tsheet, 2, data_col_range, 50, data, 126, 3); // 提取文件中第2题的成绩总成绩并存入新的sheet中
	sum(sum_data, data, 126); // 计算前2题的总成绩
	extra_write(tsheet, 3, data_col_range, 21, data, 126, 4); // 提取文件中第3题的成绩总成绩并存入新的sheet中
	sum(sum_data, data, 126); // 计算前3题的总成绩
	extra_write(tsheet, 4, data_col_range, 1, data, 126, 5); // 提取文件中第4题的成绩总成绩并存入新的sheet中
	sum(sum_data, data, 126); // 计算前4题的总成绩
	extra_write(tsheet, 5, data_col_range, 5, data, 126, 6); // 提取文件中第5题的成绩总成绩并存入新的sheet中
	sum(sum_data, data, 126); // 计算前5题的总成绩
	write_col_data(tsheet, 7, sum_data, 126); // 将总成绩写入新的sheet
	// 计算百分制成绩
	for (int i = 0; i < 126; i++) {
		data[i] = sum_data[i] * 35 / 200 + 65; // 这里用data储存修订成绩
		sum_data[i] = sum_data[i] / 2;
	}
	write_col_data(tsheet, 8, sum_data, 126); // 将百分制成绩写入sheet
	write_col_data(tsheet, 9, data, 126); // 将修订成绩写入sheet
	//统计成绩段并打印
	int intervals[5] = { 0 }; //各分数段人数
	double best_score[10] = { 0 }; //成绩较好的同学的成绩
	int ix[10] = { -1 }; //成绩较好的同学在表中的行数
	statistics(sum_data, intervals, 126, best_score, ix);
	print_interval(intervals);
	int i = 0;
	// 打印较好的同学成绩
	while (best_score[i] != 0) {
		print_best(tsheet, ix[i++]+1, 10);
	}
	name_col(tsheet); // 由于第一行不能写入，我们把每一列的名字写到第二行 
	xlBookSave(tbook, L"D:\\t.xls"); // 保存新的workbook
	// 关闭workbook 
	xlBookRelease(tbook);
	//printf("\nPress any key to exit...");
	//_getch();
	return 0;
}