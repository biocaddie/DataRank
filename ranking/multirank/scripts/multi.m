clear


% %% initialization
% load_A_asdf
load_A

% n = max(subs(:, 3));
% m = max(max(subs(:, 1)), max(subs(:, 2)));
n = 100;
m = 11448;

% journal  and author look up hashmaps
load a_idx.mat
load a_names.mat
load j_idx.mat
load j_names.mat
load d_idx.mat
load d_names.mat
author_map = containers.Map(a_idx, names_list);
journal_map = containers.Map(j_idx, j_list);
dataset_map = containers.Map(d_idx, dataset_list);



%%  generate x and y
x1 = rand(m, 1);
x2 = rand(m, 1);
y = rand(n, 1);
x1 = x1./sum(x1);
x2 = x2./sum(x2);
y = y./sum(y);

% x1y = x1*y';
% x2y = x2*y';
% xx = x1*x2';


%% build r
tic
sum_r = sparse([],[],[],m,m);
for j1 = 1:n
    idx = subs(:, 3) == j1; 
    r_tmp{j1, 1} = sparse(subs(idx, 1), subs(idx, 2), vals(idx), m, m);
    sum_r = sum_r + r_tmp{j1};
end

[idx_i1, idx_i2, r_val_denominator] = find(sum_r); 

uniqueID_j1 = unique(subs(:, 1:2), 'rows');
uniqueID_j1 = sub2ind([m,m], uniqueID_j1(:, 1), uniqueID_j1(:, 2)); % element outside this ID list will be 1/n for all j1
totalID_j1 = sub2ind([m,m], subs(:, 1), subs(:, 2));

r_vals_denominator = full(sum_r(totalID_j1));
r_vals = vals ./ r_vals_denominator;


        % check results
        assert(numel(uniqueID_j1) == numel(idx_i1));
        assert(numel(vals) == sum(r_vals_denominator > 0));
        for j1 = 1:numel(uniqueID_j1)
            assert(abs(sum(r_vals(totalID_j1 == uniqueID_j1(j1))) - 1) < eps);
        end



%% build o

sum_o = sparse([],[],[],m,n);
for i1 = 1:m
    idx = subs(:, 1) == i1; 
    o_tmp{i1, 1} = sparse(subs(idx, 2), subs(idx, 3), vals(idx), m, n);
    sum_o = sum_o + o_tmp{i1};
end

[idx_i2, idx_j1, o_val_denominator] = find(sum_o); 

uniqueID_i1 = unique(subs(:, 2:3), 'rows');
uniqueID_i1 = sub2ind([m, n], uniqueID_i1(:, 1), uniqueID_i1(:, 2)); % element outside this ID list will be 1/m for all i1
totalID_i1 = sub2ind([m, n], subs(:, 2), subs(:, 3));

o_vals_denominator = full(sum_o(totalID_i1));
o_vals = vals ./ o_vals_denominator;

        % check results
        assert(numel(uniqueID_i1) == numel(idx_i2));
        assert(numel(vals) == sum(o_vals_denominator > 0));
        for i1 = 1:numel(uniqueID_i1)
            assert(abs(sum(o_vals(totalID_i1 == uniqueID_i1(i1))) - 1) < 1e-10);
        end



%% build q

sum_q = sparse([],[],[],m,n);
for i2 = 1:m
    idx = subs(:, 2) == i2; 
    q_tmp{i2, 1} = sparse(subs(idx, 1), subs(idx, 3), vals(idx), m, n);
    sum_q = sum_q + q_tmp{i2};
end

[idx_i1, idx_j1, q_val_denominator] = find(sum_q); 

uniqueID_i2 = unique([subs(:, 1), subs(:, 3)], 'rows');
uniqueID_i2 = sub2ind([m, n], uniqueID_i2(:, 1), uniqueID_i2(:, 2)); % element outside this ID list will be 1/m for all i1
totalID_i2 = sub2ind([m, n], subs(:, 1), subs(:, 3));

q_vals_denominator = full(sum_q(totalID_i2));
q_vals = vals ./ q_vals_denominator;

        % check results
        assert(numel(uniqueID_i2) == numel(idx_i1));
        assert(numel(vals) == sum(q_vals_denominator > 0));
        for i2 = 1:numel(uniqueID_i2)
            assert(abs(sum(q_vals(totalID_i2 == uniqueID_i2(i2))) - 1) < 1e-10);
        end


norm_diff = 1;
it = 0;
eps = 1e-10;

x1_bar = x1;
x2_bar = x2;
y_bar = y;

while (norm_diff > eps)
    it = it + 1;

    x1_old = x1_bar;
    x2_old = x2_bar;
    y_old = y_bar;

    %% calculate x1
    x2y = x2_old*y_old';
    tmp_xy = x2y;
    tmp_xy(uniqueID_i1) = [];
    sum_tmp_xy_over_m = sum(tmp_xy(:))/m;
    x1_bar = zeros(m,1) + sum_tmp_xy_over_m;
    for i1 = 1:m
        idx = find(subs(:, 1) == i1); 
        if(~isempty(idx))
            idx_tmp = sub2ind([m, n], subs(idx, 2), subs(idx, 3));
            x1_bar(i1) = o_vals(idx)' * x2y(idx_tmp) + sum_tmp_xy_over_m;
        end
    end


    %% calculate x2
    x1y = x1_bar*y_old';
    tmp_xy = x1y;
    tmp_xy(uniqueID_i2) = [];
    sum_tmp_xy_over_m = sum(tmp_xy(:))/m;
    x2_bar = zeros(m,1) + sum_tmp_xy_over_m;
    for i2 = 1:m
        idx = find(subs(:, 2) == i2); 
        if(~isempty(idx))
            idx_tmp = sub2ind([m, n], subs(idx, 1), subs(idx, 3));
            x2_bar(i2) = q_vals(idx)' * x1y(idx_tmp) + sum_tmp_xy_over_m;
        end
    end

    
    %% calculate y
    xx = x1_bar*x2_bar';
    tmp_xx = xx;
    tmp_xx(uniqueID_j1) = [];
    sum_tmp_xx_over_n = sum(tmp_xx(:))/n;
    y_bar = zeros(n,1) + sum_tmp_xx_over_n;
    for j1 = 1:n
        idx = find(subs(:, 3) == j1); 
        if(~isempty(idx))
            idx_tmp = sub2ind([m, m], subs(idx, 1), subs(idx, 2));
            y_bar(j1) = r_vals(idx)' * xx(idx_tmp) + sum_tmp_xx_over_n;
        end
    end    

    fprintf('x1 norm %12.12f \n', norm(x1_old-x1_bar));
    fprintf('x2 norm %12.12f \n', norm(x2_old-x2_bar));
    fprintf('y norm %12.12f \n', norm(y_old-y_bar));

    norm_diff = (norm(x1_old-x1_bar) + norm(x2_old-x2_bar) + norm(y_old-y_bar));
    fprintf('iteration %d with norm diff %12.12f \n', it, norm_diff);
end

toc

% %%
% if(def_test) % validate results
%     assert(sum(abs(x_bar(:) - x_truth(:)) > 1e-10) == 0);
%     assert(sum(abs(y_bar(:) - y_truth(:)) > 1e-10) == 0);
% end



















%%%%%%% some stuff that was tried and didn't work

%%%%% alternative to multirank independence assumption
%%%% process B initialization
% v_bar = repmat(x1_bar, [1,n]);   %P(X1|Y)
% u_bar = repmat(x2_bar, [1,n]);   %P(X2|Y)
% z1_bar = repmat(x1_bar, [1,m]);   %P(X1|X2)
% z2_bar = repmat(x2_bar, [1,m]);   %P(X2|X1)
% w1_bar = repmat(y_bar, [1,m]);   %P(Y|X1)
% w2_bar = repmat(y_bar, [1,m]);   %P(Y|X2)



%% some stuff tried to calc cond probs
% load_P
% m = 11447;
% n = 100;
% P = sparse(subs(:,0), subs(:,1), vals, m, n);
% deno = repmat(sum(P,1),[m 1]);
% P_ = P ./ deno;
% P_(isnan(P_)) = 1/m;

% p_x_y = P_ ./ repmat(y_bar', [m 1]);
% p_y_x = P_ ./ repmat(x1_bar, [1 n]);

% denom = sum(p_y_x,1);
% p1 = p_y_x ./ repmat(denom, [m 1]);


% load JD.mat
% % delete index 0 row, cols and last dataset
% JD(1,:) = [];
% JD(:,1) = [];
% JD(:,11) = [];

% denom = sum(JD, 2);
% JD_norm = JD ./ repmat(denom, [1 10]);

