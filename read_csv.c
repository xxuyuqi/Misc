#include<stdio.h>
#include<string.h>
#define N 201

struct csv_mat
{
	int w, h;
	char* delimiter;
	float* data;
};

typedef struct csv_mat csv;

csv* read_csv(char* filename);

int main()
{
	csv* mat = read_csv("D:\\data\\sss.csv", ",");
	free(mat->data);
	free(mat->delimiter);
	return 0;
}

csv* read_csv(char* filename, char* delimiter)
{
	FILE* fp = fopen(filename, "r");
	if (!fp) return;
	csv* mat = (csv*)malloc(sizeof(csv));
	if (!mat)
	{
		fclose(fp);
		return;
	}
	mat->delimiter = (char*)malloc(sizeof(delimiter));
	memcpy(mat->delimiter, delimiter, sizeof(delimiter));
	char *str = (char *)malloc(N*sizeof(char));

	int col=0, row=0;
	char* tmp;
	while (fgets(str, N, fp))
	{
		if ((row == 0)&&(col==0))
		{
			tmp = strtok(str, delimiter);
			col++;
			while ((tmp = strtok(NULL, delimiter)))
				col++;
		}
		row++;
	}
	mat->w = col;
	mat->h = row;
	mat->data = (float*)calloc(mat->h * mat->w, sizeof(float));
	fseek(fp, 0, SEEK_SET);
	int i = 0;
	while (fgets(str, N, fp))
	{
		mat->data[i++] = atof(tmp);
		tmp = strtok(str, delimiter);
		mat->data[i++] = atof(tmp);
		while ((tmp = strtok(NULL, delimiter)))
			mat->data[i++] = atof(tmp);
	}
	fclose(fp);
	free(str);
	return mat;
}