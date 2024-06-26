import random

def genDieNumbers(n):
    probTransition = {'L': {'F': 0.2, 'L': 0.8}, 'F': {'F': 0.9, 'L': 0.1}}
    rolls = []
    dieTypes = []
    dieType = random.choice(['L', 'F'])
    for i in range(n):
        if dieType == 'L':
            rolls.append(random.choices([1, 2, 3, 4, 5, 6], weights = 6 * [1/10])[0])
        else:
            rolls.append(random.choices([1, 2, 3, 4, 5, 6], weights = 6 * [1/6])[0])
        dieTypes.append(dieType)
        weights = [probTransition[dieType]['L'], probTransition[dieType]['F']]
        dieType = random.choices(['L', 'F'], weights=weights)[0]
    return rolls, dieTypes
    
def hmmViterbi(n, rolls, dieTypes, probTransition, probNextDie):
    tableV = [{dieType: -float('inf') for dieType in dieTypes} for i in range(n)]
    tablePath = [{dieType: "" for dieType in dieTypes} for i in range(n)]
    for dieType in dieTypes:
        tableV[0][dieType] = (1/2) * probNextDie[dieType][rolls[0] - 1] 
        tablePath[0][dieType] = dieType
    for i in range(1, n):
        for currDieType in dieTypes:
            maxProb = -float('inf')
            bestPrevDieType = ''
            for prevDieType in dieTypes:
                transitionProb = probTransition[prevDieType][currDieType] * tableV[i - 1][prevDieType] 
                emissionProb = probNextDie[currDieType][rolls[i] - 1] 
                if emissionProb * transitionProb > maxProb:
                    maxProb = emissionProb * transitionProb
                    bestPrevDieType = prevDieType
            tableV[i][currDieType] = maxProb
            tablePath[i][currDieType] = bestPrevDieType
    return n, dieType, tableV, tablePath

def findOptimumPath(n, dieTypes, tableV, tablePath):
    lastProb = -float('inf')
    for dieType in dieTypes:
        if tableV[-1][dieType] > lastProb:
            lastProb = tableV[-1][dieType]
            lastDieType = dieType
    bestPath = [lastDieType]
    for i in range(n - 1, 0, -1):
        lastDieType = tablePath[i][lastDieType]
        bestPath.insert(0, lastDieType)
    return bestPath

def hmmViterbiOutput(rolls, die, viterbi):
    return f"Rolls {''.join(map(str, rolls))}\nDie {''.join(die)}\nViterbi {''.join(viterbi)}"

def evaluatePerformance(die, prediction): 
    FN = sum(map(lambda x, y: x == 'F' and y == 'L', die, prediction)) 
    TP = sum(map(lambda x, y: x == 'F' and y == 'F', die, prediction)) 
    FP = sum(map(lambda x, y: x == 'L' and y == 'F', die, prediction)) 
    TN = sum(map(lambda x, y: x == 'L' and y == 'L', die, prediction)) 
    return FN, TN, TP, FP

def calculateAccuracy(FN, TN, TP, FP): 
    return (TN + TP) / (FP + TP + TN + FN) 

def calculateMCC(FN, TN, TP, FP): 
    if ((FP+TP) * (FN+TP) * (FP+TN) * (FN+TN)) ** (1/2) != 0: 
        return (TN*TP-FN*FP) / (((FP+TP) * (FN+TP) * (FP+TN) * (FN+TN)) ** (1/2))
    return 0

def performanceOfViterbi(dieTypes, probTransition, probNextDie):
    accuracies = [] 
    MCCs = [] 
    reps = 10
    for n in range(100, 2001, 100):
        totalMCC = 0  
        totalAccuracy = 0 
        for i in range(reps): 
            rolls, die = genDieNumbers(n) 
            num, dieType, tableV, tablePath = hmmViterbi(n, rolls, dieTypes, probTransition, probNextDie) 
            prediction = findOptimumPath(num, dieType, tableV, tablePath) 
            FN, TN, TP, FP = evaluatePerformance(die, prediction) 
            accuracy = calculateAccuracy(FN, TN, TP, FP) 
            MCC = calculateMCC(FN, TN, TP, FP)
            totalMCC += MCC
            totalAccuracy += accuracy 
        avgMCC = totalMCC/reps
        avgAccuracy = totalAccuracy/reps
        MCCs.append(avgMCC)
        accuracies.append(avgAccuracy) 
    print("size            accuracy                MCC") 
    for size, accuracy, MCC in zip(range(100, 2001, 100), accuracies, MCCs): 
        print(f"{size}\t\t{accuracy:.4f}\t\t\t{MCC:.4f}") 
        
def viterbiDecode(dieTypes, probTransition, probNextDie):
    with open("sampleOutput.txt", "w") as file: 
        for i in range(3): 
            n = 40
            rolls, die = genDieNumbers(n)
            num, dieType, tableV, tablePath = hmmViterbi(n, rolls, dieTypes, probTransition, probNextDie)
            viterbi = findOptimumPath(num, dieType, tableV, tablePath)
            output = hmmViterbiOutput(rolls, die, viterbi)
            file.write(f"{output}")
            file.write("\n------------------------------------------------\n")

def main():
    probTransition = {'L': {'F': 0.2, 'L': 0.8}, 'F': {'F': 0.9, 'L': 0.1}}
    probNextDie = {'L': 6 * [1/10], 'F': 6 * [1/6]} 
    viterbiDecode(['L', 'F'], probTransition, probNextDie)
    performanceOfViterbi(['L', 'F'], probTransition, probNextDie)

if __name__ == "__main__": 
    main()

