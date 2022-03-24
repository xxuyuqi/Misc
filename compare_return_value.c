/*比较函数返回结构体和结构体指针的时间差异
  在vs x64架构下不能运行？*/

// #define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <time.h>
#include <string.h>


struct people {
	char* name;
	int sex;
	int age;
	int* map;
};

typedef struct people pt;

pt* return_ptr_pt()
{
	pt* r = (pt*)malloc(sizeof(pt));
	/*char* temp = (char*)malloc(sizeof(char) * 10);
	strcpy_s(temp, sizeof("rj"), "rj");*/
	if (!r)
	{
		return NULL;
	}
	r->name = (char*)malloc(sizeof(char) * 10);
	if (!(r->name))
	{
		free(r);
		return NULL;
	}
	strcpy_s(r->name, sizeof("rj"), "rj");
	r->sex = 1;
	r->age = 34;
	r->map = (int*)calloc(1, sizeof(int)*100);
	return r;
}

pt return_pt()
{
	char* temp = (char*)malloc(sizeof(char) * 10);
	if (!temp)
	{
		return;
	}
	strcpy_s(temp, sizeof("rj"), "rj");
	pt r = { temp, 1,34,(int*)calloc(1, sizeof(int)*100) };
	return r;
}

int free_ptr(pt* ptr, int flag)
{
	if (ptr && ptr->map)
		free(ptr->map);
	if (ptr && ptr->name)
		free(ptr->name);
	if (flag && ptr)
		free(ptr);
	return 0;
}

int main()
{
	pt* pt_ptr = NULL;
	// time_t start1, start2, stop1, stop2;
	// start1 = time(NULL);
	clock_t start1, start2, stop1, stop2;
	start1 = clock();
	pt_ptr = return_ptr_pt();
	printf("%s, %d, %d\n", pt_ptr->name, pt_ptr->sex, pt_ptr->age);
	stop1 = clock();
	// stop1 = time(NULL);
	// start2 = time(NULL);
	start2 = clock();
	pt stru = return_pt();
	printf("%s, %d, %d\n", stru.name, stru.sex, stru.age);
	stop2 = clock();
	// stop2 = time(NULL);
	printf("ptr:%f, struct:%f\n", (double)(stop1 - start1), (double)(stop2 - start2));
	free_ptr(pt_ptr, 1);
	free_ptr(&stru, 0);
	return 0;
}