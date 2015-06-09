feature('jit',0);
feature('accel',0);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% SET PARAMS
n = 100; %number of journals
m = 13553; %number of authors
eps = 0.0001; %tolerance condition
iterations = 10; %stopping condition

load_A_py = 0;
make_O_tensor = 0;
make_R_tensor = 0;

load_O = 0;
load_R = 0;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if load_A_py == 1
    load_A %from output of python script which parses medline and dicts
    A_ = sptensor(subs, vals, [m m n]);
    A = double(A_);
    clear A_;
    fprintf('Loaded tensor A (exp 1): size %dx%dx%d...\n', m,m,n);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if load_O == 1
    fprintf('Loading tensor O...');
    tic
    % O_sp = load('O_sp.mat');
    O = load('O.mat');
    fprintf('Finished loading tensor O...');
    toc
end

if load_R == 1
    fprintf('Loading tensor R...');
    tic
    R_sp = load('R_sp.mat');
    fprintf('Finished loading tensor R...');
    toc
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if make_O_tensor==1

    fprintf('Begin calculating tensor O (over authors)...\n')
    tic
    [dangle_O, S_o] = make_dangle(A,1,m);
    toc
    fprintf('finished precomputing normalization factor and dangle matrix');

    %%% create O tensor by normalizing A by i1 dimension
    % prealloc O array
    O_sp = cell(n,1);
    O_sp(:) = {zeros(m,n)};

    tic
    for i1 = 1:m
        if mod(i1,20)==0
            toc
        end
        temp = sparse(squeeze(A(i1,:,:)));
        temp2 = bsxfun(@rdivide, temp, S_o);
        O_sp{i1} = bsxfun(@plus, temp2, dangle_O);
    end
    toc
    fprintf('Created tensor O...\n');

    % tic
    % save('O_sp.mat','O_sp', '-v7.3');
    % toc
    % fprintf('Saved tensor O...\n');

end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if make_R_tensor==1

    fprintf('Begin calculating tensor R (over journals)...\n')
    tic
    [dangle_R, S_r] = make_dangle(A,3,n);
    toc
    fprintf('finished precomputing normalization factor and dangle matrix');

    %%% create R tensor by normalizing A by j1 dimension
    % prealloc R array
    R_sp = cell(n,1);
    R_sp(:) = {zeros(m,m)};

    tic
    for j1 = 1:n
        temp = sparse(squeeze(A(:,:,j1)));
        temp2 = bsxfun(@rdivide, temp, S_r);
        R_sp{j1} = bsxfun(@plus, temp2, dangle_R);
        toc
    end
    fprintf('Created tensor R...\n');

    tic
    save('R_sp.mat','R_sp', '-v7.3');
    toc
    fprintf('Saved tensor R...\n');

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CLEAR SOME MEMORY PRIOR TO MULTIRANK
% clear A


% fprintf('initializing x, y...');
% x_old = zeros(m,1); 
% y_old = zeros(n,1);
% x_ = ones(m,1) * (1.0/m);
% y_ = ones(n,1) * (1.0/n);
% 
% 
% fprintf('starting multirank...');
% it = 0;
% if (norm(x_ - x_old) + norm(y_ - y_old) > eps) | it > iterations
%     it = it + 1;
%     x_old = x_; y_old = y_;

%     tic
%     % x_ = step2(O_sp,x_old,y_old,m);
%     x_ = step2(O,x_old,y_old,m);
%     toc
%     fprintf('step 2 for iteration %d', it);
%     % NORMALIZE X_ ?????

%     tic
%     y_ = step3(R_sp,x_old,n);
%     toc
%     fprintf('step 3 for iteration %d', it);

%     it_diff = norm(x_ - x_old) + norm(y_ - y_old);
%     fprintf('norm difference %f', it_diff);
% end

% fprintf('multirank converged after %d iterations...', it);


% save('RESULTS.mat','x_','y_');

% fprintf('saved stable vectors x and y...');