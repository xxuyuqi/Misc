#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:yq

# 运行本程序需要先安装PyPDF2 在命令行里输入pip install PyPDF2即可
import os
import os.path
import re
from tkinter.filedialog import askdirectory
from PyPDF2 import PdfFileReader


default_author_name = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'] # 没有提取到作者名字的文章赋值

# 下面期刊的名字与简称的字典，需要手动添加
journal_dic ={'International Journal of Mechanical Sciences':'IJMS',
            'Journal of Sound and Vibration':'JSV',
            'International Journal of Non-Linear Mechanics':'IJNonLinMec',
            'Applied Mathematical Modelling':'APM',
            'Mechanical Systems and Signal Processing':'MSSP',
            'Communications in Nonlinear Science and Numerical Simulation':'CNSNS',
            'Appl. Phys. Lett.':'APL',
            'Advanced Materials':'AM',
            'Computer Methods in Applied Mechanics and Engineering':'CMAME',
            'Advanced Theory and Simulations':'ATS',
            'Computers and Structures':'COMPSTRUC',
            'Extreme Mechanics Letters':'EML',
            'International Journal of RF and Microwave Computer-Aided Engineering':'IJRFMCAE',
            'International Journal of Smart and Nano Materials':'IJSNM',
            'Light: Science & Applications':'LSA',
            'INTERNATIONAL JOURNAL OF MECHANICS AND MATERIALS':'MECHMAT',
            'Nature Communications':'NC',
            'Struct Multidisc Optim':'SMO',
            'Journal of the Mechanics and Physics of Solids':'JMPS',
            'Smart Materials and Structures':'SMS',
            'Acta Mechanica Sinica':'AMS'}


def name_pdf(fn):
    with open(fn,'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
    if information.subject == None or information.subject == '':
        return -1
    try :
        jn = journal_dic[information.subject.split(',')[0]]
    except:
        jn = journal_dic[re.match(r'[^\d]+', information.subject).group(0)[:-1]]
    try :
        year = information.subject.split('(')[1][:4]
    except:
        year = re.findall(r'[^\d](19|20[^34]\d)[^\d]', information.subject)[-1]
    author = information.author.split(',')[0] if information.author != None else default_author_name.pop()
    return '-'.join([jn,year,author])+'.pdf'


if __name__ == '__main__':
    dir_n = askdirectory(title='Select the data path', initialdir='C:')
    os.chdir(dir_n)
    for f in os.listdir(dir_n):
        if f.split('.')[-1]== 'pdf':
            try :
                name = name_pdf(os.path.join(dir_n, f))
                if f == name:
                    continue
                os.rename(f,name)
            except :
                # 有些pdf提取信息实在太少，就不重新命名了，手动命名最好，或者将来可以做一个pdf内容提取
                continue 