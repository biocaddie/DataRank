

load_A
A_ = sptensor(subs, vals, [m m n]);
A = double(A_);
clear A_;


[sorted_x1_val, sorted_x1_idx] = sort(x1_bar,'descend');
a1_top15 = sorted_x1_idx(1:30);

% [sorted_x2_val, sorted_x2_idx] = sort(x2_bar,'descend');
% a2_top15 = sorted_x2_idx(1:30);

[sorted_y_val, sorted_y_idx] = sort(y_bar, 'descend');
j_top15 = sorted_y_idx(1:30);

fprintf('top x1 \n');
for iii=1:15
    disp(author_map(a1_top15(iii)))
end

% fprintf('top x2 \n');
% for iii=1:30
%     disp(author_map(a2_top15(iii)))
% end

fprintf('top journals \n');
for iii=1:10
    disp(journal_map(j_top15(iii)))
end


% for iii=1:15
%     disp(author_map(a1_top15(iii)))
%     [i,j] = find(squeeze(sum(A(a1_top15(iii),:,:)))>0);
%     for jjj=1:numel(j)
%         fprintf('\t %s \n',journal_map(i(jjj)))
%     end
% end




%test some ideas to make cond prob..
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