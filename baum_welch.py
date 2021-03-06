import numpy as np

# 状態数
state_num = 2
# 出力シンボル(この場合は 0 と 1 )
symbol = np.array([0, 1])
# 出力シンボルの数
symbol_num = len(symbol)

# これが本当の値
# 遷移確率行列
A = np.array([[0.85, 0.15], [0.12, 0.88]])
# 出力確率行列
B = np.array([[0.8, 0.2], [0.4, 0.6]])
# 初期確率
pi = np.array([1/2, 1/2])

# これはパラメータ学習の初期値
# 遷移確率行列
eA = np.array([[0.7, 0.3], [0.4, 0.6]])
# 出力確率行列
eB = np.array([[0.6, 0.4], [0.5, 0.5]])
# 初期確率
epi = np.array([1/2, 1/2])


np.random.seed(1234)

def simulate(nSteps):

    def drawFrom(probs):
        return np.where(np.random.multinomial(1,probs) == 1)[0][0]

    observations = np.zeros(nSteps)
    states = np.zeros(nSteps)
    states[0] = drawFrom(pi)
    observations[0] = drawFrom(B[states[0],:])
    for t in range(1,nSteps):
        states[t] = drawFrom(A[states[t-1],:])
        observations[t] = drawFrom(B[states[t],:])
    return observations,states

def baum_welch(obs, A, B, pi, eps = 1e-9, max_iter = 500):

    # 対数尤度保持用
    old_loglikelihood = 0.0
    # 観測系列の長さ
    n = len(obs)

    for count in range(0, max_iter):
        # E-Step
        # scaled forwardアルゴリズム
        # 変数の初期化
        alpha = np.zeros((n, state_num))
        c = np.zeros(n)

        # 初期化
        alpha[0, :] = pi[:] * B[:, obs[0]]
        c[0] = 1.0 / np.sum(alpha[0, :])
        alpha[0, :] = c[0] * alpha[0, :]

        # 再帰的計算
        for t in range(1, n):
            alpha[t, :] = np.dot(alpha[t-1, :], A) * B[:, obs[t]]
            c[t] = 1.0 / np.sum(alpha[t, :])
            alpha[t, :] = c[t] * alpha[t, :]


        # scaled backwardアルゴリズム
        # 変数の初期化
        beta = np.zeros((n, state_num))

        # 初期化
        beta[n-1, :] = c[n-1]

        # 再帰的計算
        for t in range((n-1), 0, -1):
            beta[t-1, :] = np.dot(A, (B[:, obs[t]] * beta[t, :]))
            beta[t-1, :] = c[t-1] * beta[t-1, :]



        # M-Step
        # update A
        # ちょっとダサい。
        newA = numer = denom = np.zeros((state_num, state_num))
        for t in range(0, n-1):
            numer = numer + alpha[t, :][:, np.newaxis] * A * B[:, obs[t+1]] * beta[t+1, :]
            denom = denom + alpha[t, :] * beta[t, :] / c[t]
        newA = numer / denom.T

        # update B
        # ダサい。
        newB = np.zeros((state_num, symbol_num))
        for j in range(0, state_num):
            for k in range(0, symbol_num):
                B_num = np.sum((obs[:] == symbol[k]) * alpha[:, j] * beta[:, j] / c[:])
                B_den = np.sum(alpha[:, j].T * beta[:, j] / c[:])
                newB[j, k] = B_num / B_den

        # update pi
        newpi = alpha[0, :] * beta[0, :] / c[0]

        # update new parameters
        A = newA
        B = newB
        pi = newpi

        # convergence check
        loglikelihood = - np.sum(np.log(c[:]))
        if np.abs(old_loglikelihood - loglikelihood) < eps:
            break
        old_loglikelihood = loglikelihood

        print("iter: ", count, "loglikelihood: ", loglikelihood)

    return [A, B, pi]


# 観測系列
obs, state = simulate(1000)

#obs = np.array([0, 1, 0])

eA, eB, epi = baum_welch(obs, eA, eB, epi)

print("Actual parameters")
print(A)
print(B)
print(pi)

print("Estimated parameters")
print(eA)
print(eB)
print(epi)
