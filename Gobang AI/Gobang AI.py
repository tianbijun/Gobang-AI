from enum import IntEnum
import time

AI_SEARCH_DEPTH = 4
AI_LIMITED_MOVE_NUM = 20
chess_len = 16


class CHESS_TYPE(IntEnum):
    NONE = 0,
    STWO = 1,
    LTWO = 2,
    STHREE = 3
    LTHREE = 4,
    CFOUR = 5,
    LFOUR = 6,
    LFIVE = 7,


CHESS_TYPE_NUM = 8

FIVE = CHESS_TYPE.LFIVE.value
FOUR, THREE, TWO = CHESS_TYPE.LFOUR.value, CHESS_TYPE.LTHREE.value, CHESS_TYPE.LTWO.value
SFOUR, STHREE, STWO = CHESS_TYPE.CFOUR.value, CHESS_TYPE.STHREE.value, CHESS_TYPE.STWO.value

MAX = 0x7fffffff
MIN = -1 * MAX
Mark_Five, Mark_Four, Mark_SFour = 100000, 10000, 1000
Mark_Three, Mark_SThree, Mark_Two, Mark_STwo = 100, 10, 8, 2

listAI = []
listHuman = []
list_all = []


class gobang_AI():
    def __init__(self, chess_len):
        self.chess_len = chess_len
        self.record = [[[0, 0, 0, 0] for x in range(chess_len)] for y in range(chess_len)]
        self.count = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(2)]

    # maxminαβ剪枝算法
    def find(self, map, turn, AI_SEARCH_DEPTH):
        self.maxAI_SEARCH_DEPTH = AI_SEARCH_DEPTH
        self.bestPos = None
        score = self.maxmin(map, turn, AI_SEARCH_DEPTH)
        print(self.bestPos)
        x, y = self.bestPos
        return score, x, y

    def maxmin(self, map, player, AI_SEARCH_DEPTH, alpha=MIN, beta=MAX):
        Mark = self.evaluate(map, player)
        if AI_SEARCH_DEPTH <= 0 or abs(Mark) >= Mark_Five:
            return Mark

        pos = self.genmove(map, player)
        bestPos = None
        self.alpha += len(pos)

        if len(pos) == 0:
            return Mark

        for _, x, y in pos:
            map[y][x] = player

            if player == 1:
                opTurn = 2
            else:
                opTurn = 1

            Mark = - self.maxmin(map, opTurn, AI_SEARCH_DEPTH - 1, -beta, -alpha)

            map[y][x] = 0
            self.belta += 1

            # alpha/beta pruning
            if Mark > alpha:
                alpha = Mark
                bestPos = (x, y)
                if alpha >= beta:
                    break

        if AI_SEARCH_DEPTH == self.maxAI_SEARCH_DEPTH and bestPos:
            self.bestPos = bestPos

        return alpha

    # 确定下棋位置，并输出相关信息
    def findBestChess(self, map, player):
        time1 = time.time()
        self.alpha = 0
        self.belta = 0
        score, x, y = self.find(map, player, AI_SEARCH_DEPTH)
        time2 = time.time()
        print('time[%.2f] ,(%d, %d), score[%d], alpha[%d] belta[%d]' % (
            (time2 - time1), x, y, score, self.alpha, self.belta))
        return (x, y)

    # 评估当前棋局的分数
    def evaluate(self, map, player, checkWin=False):  # 评价函数实现
        self.reset()
        if player == 1:
            mine = 1
            enemy = 2
        else:
            mine = 2
            enemy = 1
        for y in range(self.chess_len):
            for x in range(self.chess_len):
                if map[y][x] == mine:
                    self.checkpoint(map, x, y, mine, enemy)
                elif map[y][x] == enemy:
                    self.checkpoint(map, x, y, enemy, mine)

        myCount = self.count[mine - 1]
        enemyCount = self.count[enemy - 1]
        if checkWin:
            return myCount[FIVE] > 0
        else:
            mscore, oscore = self.getScore(myCount, enemyCount)
            return (mscore - oscore)

    # 对一个位置的4个方向进行检查
    def checkpoint(self, map, x, y, mine, enemy, count=None):  # 对一个位置四个方向进行检查
        offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        ignoreRecord = True
        if count is None:
            count = self.count[mine - 1]
            ignoreRecord = False
        for i in range(4):
            if self.record[y][x][i] == 0 or ignoreRecord:
                self.analysisLine(map, x, y, i, offset[i], mine, enemy, count)

    # 调用评估函数前清除之前的统计数据
    def reset(self):
        for y in range(self.chess_len):
            for x in range(self.chess_len):
                for i in range(4):
                    self.record[y][x][i] = 0
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

    # 判断是否有人获胜
    def isWin(self, board, turn):
        return self.evaluate(board, turn, True)

    # 获取下己方或对方棋子时形成的棋局的评分，然后将评分较高的位置加入单独的列表中
    def evaluatePointScore(self, map, x, y, here, enemy):
        for i in range(len(self.count)):
            for j in range(len(self.count[0])):
                self.count[i][j] = 0

        map[y][x] = here
        self.checkpoint(map, x, y, here, enemy, self.count[here - 1])
        mineCount = self.count[here - 1]
        map[y][x] = enemy
        self.checkpoint(map, x, y, enemy, here, self.count[enemy - 1])
        enemyCount = self.count[enemy - 1]
        map[y][x] = 0

        mscore = self.getpointScore(mineCount)
        oscore = self.getpointScore(enemyCount)

        return (mscore, oscore)

    # 搜索空间的剪枝，只考虑部分空位置（剪去了没必要考虑的位置，减小了搜索空间）
    def hasNeighbor(self, map, x, y, radius):
        start_x, end_x = (x - radius), (x + radius)
        start_y, end_y = (y - radius), (y + radius)

        for i in range(start_y, end_y + 1):
            for j in range(start_x, end_x + 1):
                if i >= 0 and i < self.chess_len and j >= 0 and j < self.chess_len:
                    if map[i][j] != 0:
                        return True
        return False

    # 获取位置的评分，后续只选择有利位置下棋（位置剪枝）
    def genmove(self, map, player):
        fives = []
        mfours, ofours = [], []
        msfours, osfours = [], []
        if player == 1:
            mine = 1
            opponent = 2
        else:
            mine = 2
            opponent = 1

        pos = []
        radius = 1

        for y in range(self.chess_len):
            for x in range(self.chess_len):
                if map[y][x] == 0 and self.hasNeighbor(map, x, y, radius):
                    mscore, oscore = self.evaluatePointScore(map, x, y, mine, opponent)
                    point = (max(mscore, oscore), x, y)

                    if mscore >= Mark_Five or oscore >= Mark_Five:
                        fives.append(point)
                    elif mscore >= Mark_Four:
                        mfours.append(point)
                    elif oscore >= Mark_Four:
                        ofours.append(point)
                    elif mscore >= Mark_SFour:
                        msfours.append(point)
                    elif oscore >= Mark_SFour:
                        osfours.append(point)

                    pos.append(point)

        if len(fives) > 0: return fives

        if len(mfours) > 0: return mfours

        if len(ofours) > 0:
            if len(msfours) == 0:
                return ofours
            else:
                return ofours + msfours

        pos.sort(reverse=True)

        if self.maxAI_SEARCH_DEPTH > 2 and len(pos) > AI_LIMITED_MOVE_NUM:
            pos = pos[:AI_LIMITED_MOVE_NUM]
        return pos

    # 获取单个位置的评分
    def getpointScore(self, count):
        score = 0
        if count[FIVE] > 0:
            return Mark_Five

        if count[FOUR] > 0:
            return Mark_Four

        if count[SFOUR] > 1:
            score += count[SFOUR] * Mark_SFour
        elif count[SFOUR] > 0 and count[THREE] > 0:
            score += count[SFOUR] * Mark_SFour
        elif count[SFOUR] > 0:
            score += Mark_Three

        if count[THREE] > 1:
            score += 5 * Mark_Three
        elif count[THREE] > 0:
            score += Mark_Three

        if count[STHREE] > 0:
            score += count[STHREE] * Mark_SThree
        if count[TWO] > 0:
            score += count[TWO] * Mark_Two
        if count[STWO] > 0:
            score += count[STWO] * Mark_STwo

        return score

    # 单个位置的评估函数
    def getScore(self, mine_count, opponent_count):
        mscore, oscore = 0, 0
        if mine_count[FIVE] > 0:
            return (Mark_Five, 0)
        if opponent_count[FIVE] > 0:
            return (0, Mark_Five)
        if mine_count[SFOUR] >= 2:
            mine_count[FOUR] += 1
        if opponent_count[SFOUR] >= 2:
            opponent_count[FOUR] += 1
        if mine_count[FOUR] > 0:
            return (9050, 0)
        if mine_count[SFOUR] > 0:
            return (9040, 0)
        if opponent_count[FOUR] > 0:
            return (0, 9030)
        if opponent_count[SFOUR] > 0 and opponent_count[THREE] > 0:
            return (0, 9020)
        if mine_count[THREE] > 0 and opponent_count[SFOUR] == 0:
            return (9010, 0)
        if (opponent_count[THREE] > 1 and mine_count[THREE] == 0 and mine_count[STHREE] == 0):
            return (0, 9000)
        if opponent_count[SFOUR] > 0:
            oscore += 400
        if mine_count[THREE] > 1:
            mscore += 500
        elif mine_count[THREE] > 0:
            mscore += 100
        if opponent_count[THREE] > 1:
            oscore += 2000
        elif opponent_count[THREE] > 0:
            oscore += 400
        if mine_count[STHREE] > 0:
            mscore += mine_count[STHREE] * 10
        if opponent_count[STHREE] > 0:
            oscore += opponent_count[STHREE] * 10
        if mine_count[TWO] > 0:
            mscore += mine_count[TWO] * 6
        if opponent_count[TWO] > 0:
            oscore += opponent_count[TWO] * 6
        if mine_count[STWO] > 0:
            mscore += mine_count[STWO] * 2
        if opponent_count[STWO] > 0:
            oscore += opponent_count[STWO] * 2
        return (mscore, oscore)

    # 获取长度为9的线
    def getLine(self, board, x, y, dir_offset, mine, opponent):
        line = [0 for i in range(9)]

        tmp_x = x + (-5 * dir_offset[0])
        tmp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if (tmp_x < 0 or tmp_x >= self.chess_len or
                    tmp_y < 0 or tmp_y >= self.chess_len):
                line[i] = opponent
            else:
                line[i] = board[tmp_y][tmp_x]

        return line

    # 判断一条线上自己的棋能形成的棋型
    def analysisLine(self, map, x, y, index, dir, mine, opponent, CNT):

        # 标记已经检测过，需要跳过的棋子
        def setRecord(self, x, y, left, right, index, offset):
            tmp_x = x + (-5 + left) * offset[0]
            tmp_y = y + (-5 + left) * offset[1]
            for i in range(left, right + 1):
                tmp_x += offset[0]
                tmp_y += offset[1]
                self.record[tmp_y][tmp_x][index] = 1

        Empty = 0
        leftIdx, rightIdx = 4, 4

        line = self.getLine(map, x, y, dir, mine, opponent)

        while rightIdx < 8:
            if line[rightIdx + 1] != mine:
                break
            rightIdx += 1
        while leftIdx > 0:
            if line[leftIdx - 1] != mine:
                break
            leftIdx -= 1

        leftRange, rightRange = leftIdx, rightIdx
        while rightRange < 8:
            if line[rightRange + 1] == opponent:
                break
            rightRange += 1
        while leftRange > 0:
            if line[leftRange - 1] == opponent:
                break
            leftRange -= 1

        RANGE = rightRange - leftRange + 1
        if RANGE < 5:
            setRecord(self, x, y, leftRange, rightRange, index, dir)
            return CHESS_TYPE.NONE

        setRecord(self, x, y, leftIdx, rightIdx, index, dir)

        Mrange = rightIdx - leftIdx + 1

        if Mrange >= 5:
            CNT[FIVE] += 1

        if Mrange == 4:
            lEmpty = rEmpty = False
            if line[leftIdx - 1] == Empty:
                lEmpty = True
            if line[rightIdx + 1] == Empty:
                rEmpty = True
            if lEmpty and rEmpty:
                CNT[FOUR] += 1
            elif lEmpty or rEmpty:
                CNT[SFOUR] += 1

        if Mrange == 3:
            lEmpty = rEmpty = False
            lFour = rFour = False
            if line[leftIdx - 1] == Empty:
                if line[leftIdx - 2] == mine:
                    setRecord(self, x, y, leftIdx - 2, leftIdx - 1, index, dir)
                    CNT[SFOUR] += 1
                    lFour = True
                lEmpty = True

            if line[rightIdx + 1] == Empty:
                if line[rightIdx + 2] == mine:
                    setRecord(self, x, y, rightIdx + 1, rightIdx + 2, index, dir)
                    CNT[SFOUR] += 1
                    rFour = True
                rEmpty = True

            if lFour or rFour:
                pass
            elif lEmpty and rEmpty:
                if RANGE > 5:
                    CNT[THREE] += 1
                else:
                    CNT[STHREE] += 1
            elif lEmpty or rEmpty:
                CNT[STHREE] += 1

        if Mrange == 2:
            lEmpty = rEmpty = False
            lThree = rThree = False
            if line[leftIdx - 1] == Empty:
                if line[leftIdx - 2] == mine:
                    setRecord(self, x, y, leftIdx - 2, leftIdx - 1, index, dir)
                    if line[leftIdx - 3] == Empty:
                        if line[rightIdx + 1] == Empty:
                            CNT[THREE] += 1
                        else:
                            CNT[STHREE] += 1
                        lThree = True
                    elif line[leftIdx - 3] == opponent:
                        if line[rightIdx + 1] == Empty:
                            CNT[STHREE] += 1
                            lThree = True

                lEmpty = True

            if line[rightIdx + 1] == Empty:
                if line[rightIdx + 2] == mine:
                    if line[rightIdx + 3] == mine:
                        setRecord(self, x, y, rightIdx + 1, rightIdx + 2, index, dir)
                        CNT[SFOUR] += 1
                        rThree = True
                    elif line[rightIdx + 3] == Empty:
                        if lEmpty:
                            CNT[THREE] += 1
                        else:
                            CNT[STHREE] += 1
                        rThree = True
                    elif lEmpty:
                        CNT[STHREE] += 1
                        rThree = True

                rEmpty = True

            if lThree or rThree:
                pass
            elif lEmpty and rEmpty:
                CNT[TWO] += 1
            elif lEmpty or rEmpty:  #
                CNT[STWO] += 1

        if Mrange == 1:
            lEmpty = rEmpty = False
            if line[leftIdx - 1] == Empty:
                if line[leftIdx - 2] == mine:
                    if line[leftIdx - 3] == Empty:
                        if line[rightIdx + 1] == opponent:
                            CNT[STWO] += 1
                lEmpty = True

            if line[rightIdx + 1] == Empty:
                if line[rightIdx + 2] == mine:
                    if line[rightIdx + 3] == Empty:
                        if lEmpty:
                            CNT[TWO] += 1
                        else:
                            CNT[STWO] += 1
                elif line[rightIdx + 2] == Empty:
                    if line[rightIdx + 3] == mine and line[rightIdx + 4] == Empty:
                        CNT[TWO] += 1

        return CHESS_TYPE.NONE


def ai(listAI, listHuman, list_all):
    if len(listHuman) == 0:
        return 7, 7
    AI = gobang_AI(chess_len)
    map = [[0 for x in range(chess_len)] for y in range(chess_len)]
    for x, y in listAI:
        map[y][x] = 1
    for x, y in listHuman:
        map[y][x] = 2
    x, y = AI.findBestChess(map, 1)
    return x, y


ai(listAI, listHuman, list_all)

