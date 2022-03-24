function [] = p_b(chrom, Fitness, ginp)
% This matlab code reuses the code written in python

% chrom is the chromulation's gene array data to plot, Fitness is the Fitness
% array of every individuals. ginp is the index of individual to save .inp
% files
if nargin < 3
    ginp=[];
else
    if count(py.sys.path,'D:\matlab\mcode') == 0
        insert(py.sys.path,int32(0),'D:\matlab\mcode');
    end
    ms = py.importlib.import_module('ms');
    model_f = 'D:\matlab\model8.inp';
end
for i=1:size(chrom,1)
    a = squeeze(chrom(i,:,:));
    ar = [a, flip(a,2)];
    bor = ones([1,80],'int8');
    ar = [bor;ar;bor];
    figure()
    imshow(-ar,[-1,0],'Colormap',summer,'InitialMagnification','fit')
    title(num2str(Fitness(i,:)))
    if ismember(i,ginp)
        inpf = join(['D:\matlab\inp\Ind-',num2str(i),'.inp']);
        ms.file_process(inpf,model_f,ms.assem_array(a));
    end
end
