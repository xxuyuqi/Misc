clear;
E=2.0e5; % 弹性模量
nu=0.3; % 泊松比
t=1; % 厚度
nodes = readmatrix("./nodes.csv"); % 节点坐标
elements = readmatrix("./element.csv"); % 单元
ele_num = length(elements); % 单元数量
node_num = length(nodes); % 节点数
dof = 2 * node_num; % 自由度数
k = zeros(dof,dof); % 总体刚度矩阵
f = f_vector(dof, nodes, t); % 载荷向量
all_dofs = 1:dof; % 所有的自由度
fixed_dofs = [3,5,35,37,39,41,43,45,47,9,14,80,82,84,86,88,90,92,16,18]; % 固定的自由度
free_dofs = setdiff(all_dofs, fixed_dofs); % 自由的自由度
u = zeros(dof,1); % 位移向量
% 单刚集成总刚
for i=1:ele_num
    dofs_ix = zeros(8,1); % 储存一个单元四个节点的八个自由度
    for j=1:4
        dofs_ix([2*j-1,2*j]) =  [elements(i,j+1)*2-1,elements(i,j+1)*2]; % 一个节点的自由度是2*node-1和2*node
    end
    k(dofs_ix,dofs_ix) = k(dofs_ix,dofs_ix) + ElementStiffness(nodes(elements(i,2:5),2:3),E,nu,t,0); %集成总刚
end
% 求解线性方程组，消去固定的自由度，总刚失去奇异性
u(free_dofs,:) = k(free_dofs,free_dofs) \ f(free_dofs,:);      
u(fixed_dofs,:)= 0;
sigma_y(u,nodes,elements,E,nu,0);

function [N1,N2,N3,N4] = shapefunction(r,s)
% 形函数
    N1 = 1 / 4 * (1 - r) * (1 - s);
    N2 = 1 / 4 * (1 + r) * (1 - s);
    N3 = 1 / 4 * (1 + r) * (1 + s);
    N4 = 1 / 4 * (1 - r) * (1 + s);
end   

function [dNdr] = DiffNdr(r,s)
%求dNi/dr
    dN1dr = 1 / 4 * (-1) * (1 - s);
    dN2dr = 1 / 4 * (1) * (1 - s);
    dN3dr = 1 / 4 * (1) * (1 + s);
    dN4dr = 1 / 4 * (-1) * (1 + s);
    dNdr = [dN1dr,dN2dr,dN3dr,dN4dr];
end


function [dNds] = DiffNds(r,s)
%求dNi/ds
    dN1ds = 1 / 4 * (1 - r) * (-1);
    dN2ds = 1 / 4 * (1 + r) * (-1);
    dN3ds = 1 / 4 * (1 + r) * (1);
    dN4ds = 1 / 4 * (1 - r) * (1);
    dNds = [dN1ds, dN2ds, dN3ds, dN4ds];
end

function [Jinv,Jdet] = Jacobian(node_ele,r,s)
%求J,Jinv,Jdet
    dNdr = DiffNdr(r,s);
    dNds = DiffNds(r,s);
    J = [dNdr;dNds]*node_ele;
    Jdet = det(J);
    Jinv = inv(J);
end

function [B] = Bmatrix(r,s,Jinv)
% 求B
    dNdr = DiffNdr(r, s);
    dNds = DiffNds(r, s);

    B1 = [1,0,0,0;0,0,0,1;0,1,1,0];
    B2 = zeros(4);
    B2(1:2,1:2) = Jinv;
    B2(3:4,3:4) = Jinv;
    B3 = zeros(4,8);
    B3(1,1) = dNdr(1);
    B3(1,3) = dNdr(2);
    B3(1,5) = dNdr(3);
    B3(1,7) = dNdr(4);
    B3(2,1) = dNds(1);
    B3(2,3) = dNds(2);
    B3(2,5) = dNds(3);
    B3(2,7) = dNds(4);
    B3(3,2) = dNdr(1);
    B3(3,4) = dNdr(2);
    B3(3,6) = dNdr(3);
    B3(3,8) = dNdr(4);
    B3(4,2) = dNds(1);
    B3(4,4) = dNds(2);
    B3(4,6) = dNds(3);
    B3(4,8) = dNds(4);

    B = B1*B2*B3;
end

function [D] = stiffnessMatrix(E,nu,pt)
if pt==0 % 平面应力
    E0 = E;
    nu0 = nu;
else % 平面应变
    E0 = E/(1-nu^2);
    nu0 = nu/(1-nu);
end
D0 = E0/(1-nu0^2);
D = D0*[1,nu0,0;nu0,1,0;0,0,(1-nu0)/2];
end

function [ke] = ElementStiffness(node_ele,E,nu,t,pt)
ke = zeros(8);
D = stiffnessMatrix(E,nu,pt);
% 2×2高斯积分，积分点[-1/sqrt(3),1/sqrt(3)]，权重[1.0,1.0]
int_point = [-1/sqrt(3),1/sqrt(3)];
w = [1.0,1.0];
for i1 = 1:2
    for j = 1:2
        [Jinv,Jdet] = Jacobian(node_ele, int_point(i1), int_point(j));
        B = Bmatrix(int_point(i1), int_point(j), Jinv);
        ke =ke + B'*D*B*abs(Jdet)*t*w(i1)*w(j);
    end
end
end

function [f] = f_vector(dof,nodes, t)
q = 10; % 载荷10MPa
f = zeros(dof,1);
f(4) = 1/2*q*(nodes(14,2)-nodes(2,2))*t; % 2号节点2方向
f(28) = 1/2*q*(nodes(14,2)-nodes(2,2))*t + 1/2*q*(nodes(13,2)-nodes(14,2))*t; % 14号节点2方向
f(26) = 1/2*q*(nodes(13,2)-nodes(14,2))*t + 1/2*q*(nodes(12,2)-nodes(13,2))*t; % 13号节点2方向
f(24) = 1/2*q*(nodes(12,2)-nodes(13,2))*t + 1/2*q*(nodes(1,2)-nodes(12,2))*t; % 12号节点2方向
f(2) = 1/2*q*(nodes(1,2)-nodes(12,2))*t + 1/2*q*(nodes(11,2)-nodes(1,2))*t; % 1号节点2方向
f(22) = 1/2*q*(nodes(11,2)-nodes(1,2))*t; % 11号节点2方向
end

function sigma_y(u,nodes,elements,E,nu,p)
ele_ix = [42,48,54,60,66,72,78,84,85]; % y=0经过的单元号
sigma_y = [];
x = [];
stress_pts = -1:0.1:1; % 局部坐标
for ix = ele_ix
    dofs_ix = zeros(8,1); % 储存一个单元四个节点的八个自由度
        for j=1:4
            dofs_ix([2*j-1,2*j]) =  [elements(ix,j+1)*2-1,elements(ix,j+1)*2];
        end
    for pt = stress_pts
        if ix~=85 % 当沿着y=0,x增大方向，除了85号单元，其他单元局部坐标都是r=1,s从-1到1变化，可以从单元的节点顺序看出来
            [Jinv,~] = Jacobian(nodes(elements(ix,2:5),2:3), 1, pt);
            B = Bmatrix(1, pt, Jinv);
            D = stiffnessMatrix(E,nu,p);
            stress = D*B*u(dofs_ix,:);
            sigma_y = [sigma_y,stress(2,:)];
            x = [x,nodes(elements(ix,3),2)+(nodes(elements(ix,4),2)-nodes(elements(ix,3),2))*(pt+1)/2];
        else % 85号单元局部坐标r=-1:1,s=-1
            [Jinv,~] = Jacobian(nodes(elements(ix,2:5),2:3), pt, -1);
            B = Bmatrix(pt, -1, Jinv);
            D = stiffnessMatrix(E,nu,p);
            stress = D*B*u(dofs_ix,:); % S=D*B*U
            sigma_y = [sigma_y,stress(2,:)]; % stress = [sigma_x,sigma_y,sigma_xy];
            x = [x,nodes(elements(ix,2),2)+(nodes(elements(ix,3),2)-nodes(elements(ix,2),2))*(pt+1)/2]; % x从局部坐标到自然坐标的转换
        end
    end
end
plot(x,sigma_y)
end