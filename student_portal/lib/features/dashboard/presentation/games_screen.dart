import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';
import 'dart:async';
import 'dart:math';

class GamesScreen extends StatelessWidget {
  const GamesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Educational Games')),
      body: GridView.count(
        padding: const EdgeInsets.all(24),
        crossAxisCount: 2,
        mainAxisSpacing: 20,
        crossAxisSpacing: 20,
        children: [
          _GameCard(
            title: 'Tic Tac Toe',
            icon: Icons.grid_3x3_rounded,
            color: Colors.orange,
            onTap: () => context.push('/games/tictactoe'),
          ),
          _GameCard(
            title: 'Math Quiz',
            icon: Icons.calculate_rounded,
            color: Colors.blue,
            onTap: () => context.push('/games/math-quiz'),
          ),
          _GameCard(
            title: 'Word Search',
            icon: Icons.search_rounded,
            color: Colors.green,
            onTap: () => context.push('/games/word-search'),
          ),
          _GameCard(
            title: 'Memory Match',
            icon: Icons.psychology_rounded,
            color: Colors.purple,
            onTap: () => context.push('/games/memory-match'),
          ),
        ],
      ),
    );
  }
}

class _GameCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _GameCard({required this.title, required this.icon, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 50, color: color),
            const SizedBox(height: 12),
            Text(title, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}

// ======================== TIC TAC TOE ========================
class TicTacToeGame extends StatefulWidget {
  const TicTacToeGame({super.key});

  @override
  State<TicTacToeGame> createState() => _TicTacToeGameState();
}

class _TicTacToeGameState extends State<TicTacToeGame> {
  List<String> displayElement = ['', '', '', '', '', '', '', '', ''];
  bool oTurn = true;
  String winner = '';
  int filledBoxes = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tic Tac Toe')),
      body: Column(
        children: [
          const SizedBox(height: 40),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Text(
              winner.isNotEmpty ? winner : (oTurn ? "Player O's Turn" : "Player X's Turn"),
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            flex: 3,
            child: GridView.builder(
              padding: const EdgeInsets.all(24),
              itemCount: 9,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3),
              itemBuilder: (BuildContext context, int index) {
                return GestureDetector(
                  onTap: () => _tapped(index),
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey[300]!),
                    ),
                    child: Center(
                      child: Text(
                        displayElement[index],
                        style: TextStyle(
                          fontSize: 40,
                          fontWeight: FontWeight.bold,
                          color: displayElement[index] == 'O' ? Colors.blue : Colors.red,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(40),
            child: ElevatedButton(
              onPressed: _clearBoard,
              child: const Text('Reset Game'),
            ),
          ),
        ],
      ),
    );
  }

  void _tapped(int index) {
    if (winner.isNotEmpty || displayElement[index].isNotEmpty) return;

    setState(() {
      if (oTurn) {
        displayElement[index] = 'O';
      } else {
        displayElement[index] = 'X';
      }

      filledBoxes++;
      oTurn = !oTurn;
      _checkWinner();
    });
  }

  void _checkWinner() {
    String foundWinner = '';
    if (displayElement[0] == displayElement[1] && displayElement[0] == displayElement[2] && displayElement[0] != '') foundWinner = 'Player ${displayElement[0]} Wins!';
    if (displayElement[3] == displayElement[4] && displayElement[3] == displayElement[5] && displayElement[3] != '') foundWinner = 'Player ${displayElement[3]} Wins!';
    if (displayElement[6] == displayElement[7] && displayElement[6] == displayElement[8] && displayElement[6] != '') foundWinner = 'Player ${displayElement[6]} Wins!';
    if (displayElement[0] == displayElement[3] && displayElement[0] == displayElement[6] && displayElement[0] != '') foundWinner = 'Player ${displayElement[0]} Wins!';
    if (displayElement[1] == displayElement[4] && displayElement[1] == displayElement[7] && displayElement[1] != '') foundWinner = 'Player ${displayElement[1]} Wins!';
    if (displayElement[2] == displayElement[5] && displayElement[2] == displayElement[8] && displayElement[2] != '') foundWinner = 'Player ${displayElement[2]} Wins!';
    if (displayElement[0] == displayElement[4] && displayElement[0] == displayElement[8] && displayElement[0] != '') foundWinner = 'Player ${displayElement[0]} Wins!';
    if (displayElement[2] == displayElement[4] && displayElement[2] == displayElement[6] && displayElement[2] != '') foundWinner = 'Player ${displayElement[2]} Wins!';
    
    if (foundWinner.isNotEmpty) {
      winner = foundWinner;
      _showWinDialog(winner);
    } else if (filledBoxes == 9) {
      winner = 'Draw!';
      _showWinDialog(winner);
    }
  }

  void _showWinDialog(String text) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: Text(text),
        actions: [
          TextButton(
            onPressed: () {
              _clearBoard();
              Navigator.pop(context);
            },
            child: const Text('Play Again'),
          ),
        ],
      ),
    );
  }

  void _clearBoard() {
    setState(() {
      for (int i = 0; i < 9; i++) displayElement[i] = '';
      winner = '';
      filledBoxes = 0;
    });
  }
}

// ======================== MATH QUIZ ========================
class MathQuizGame extends StatefulWidget {
  const MathQuizGame({super.key});

  @override
  State<MathQuizGame> createState() => _MathQuizGameState();
}

class _MathQuizGameState extends State<MathQuizGame> {
  int num1 = 0;
  int num2 = 0;
  String operator = '+';
  int answer = 0;
  int score = 0;
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _generateQuestion();
  }

  void _generateQuestion() {
    final random = Random();
    num1 = random.nextInt(20) + 1;
    num2 = random.nextInt(20) + 1;
    final opIndex = random.nextInt(3);
    if (opIndex == 0) {
      operator = '+';
      answer = num1 + num2;
    } else if (opIndex == 1) {
      operator = '-';
      if (num1 < num2) {
        final temp = num1;
        num1 = num2;
        num2 = temp;
      }
      answer = num1 - num2;
    } else {
      operator = '×';
      num1 = random.nextInt(10) + 1;
      num2 = random.nextInt(10) + 1;
      answer = num1 * num2;
    }
  }

  void _checkAnswer() {
    if (_controller.text == answer.toString()) {
      setState(() {
        score++;
        _generateQuestion();
        _controller.clear();
      });
    } else {
      _showGameOver();
    }
  }

  void _showGameOver() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Game Over!'),
        content: Text('Wrong Answer! The correct answer was $answer.\nYour final score: $score'),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                score = 0;
                _generateQuestion();
                _controller.clear();
              });
              Navigator.pop(context);
            },
            child: const Text('Try Again'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              context.pop(); // Go back to games screen
            },
            child: const Text('Exit'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Math Quiz')),
      body: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          children: [
            Text('Score: $score', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const Spacer(),
            Text('$num1 $operator $num2 = ?', style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold)),
            const SizedBox(height: 40),
            TextField(
              controller: _controller,
              keyboardType: TextInputType.number,
              autofocus: true,
              style: const TextStyle(fontSize: 32),
              textAlign: TextAlign.center,
              decoration: const InputDecoration(hintText: 'Answer'),
              onSubmitted: (_) => _checkAnswer(),
            ),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: _checkAnswer, child: const Text('Submit')),
            const Spacer(flex: 2),
          ],
        ),
      ),
    );
  }
}

// ======================== MEMORY MATCH ========================
class MemoryMatchGame extends StatefulWidget {
  const MemoryMatchGame({super.key});

  @override
  State<MemoryMatchGame> createState() => _MemoryMatchGameState();
}

class _MemoryMatchGameState extends State<MemoryMatchGame> {
  final List<String> icons = ['🍎', '🍌', '🍇', '🍉', '🍒', '🍓', '🍑', '🍍'];
  late List<String> cards;
  late List<bool> visible;
  int? firstIndex;
  bool isProcessing = false;

  @override
  void initState() {
    super.initState();
    _startNewGame();
  }

  void _startNewGame() {
    cards = [...icons, ...icons];
    cards.shuffle();
    visible = List.filled(cards.length, false);
    firstIndex = null;
    isProcessing = false;
  }

  void _onCardTap(int index) {
    if (isProcessing || visible[index] || index == firstIndex) return;

    setState(() => visible[index] = true);

    if (firstIndex == null) {
      firstIndex = index;
    } else {
      if (cards[firstIndex!] == cards[index]) {
        firstIndex = null;
        if (visible.every((v) => v)) {
          _showWinDialog();
        }
      } else {
        isProcessing = true;
        Timer(const Duration(seconds: 1), () {
          setState(() {
            visible[firstIndex!] = false;
            visible[index] = false;
            firstIndex = null;
            isProcessing = false;
          });
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Memory Match')),
      body: GridView.builder(
        padding: const EdgeInsets.all(24),
        itemCount: cards.length,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4, crossAxisSpacing: 10, mainAxisSpacing: 10),
        itemBuilder: (context, index) {
          return GestureDetector(
            onTap: () => _onCardTap(index),
            child: Card(
              color: visible[index] ? Colors.white : AppTheme.primaryBlue,
              child: Center(
                child: Text(
                  visible[index] ? cards[index] : '?',
                  style: TextStyle(
                      fontSize: 24,
                      color: visible[index] ? Colors.black : Colors.white),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  void _showWinDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Congratulations!'),
        content: const Text('You found all pairs!'),
        actions: [
          TextButton(
            onPressed: () {
              setState(() => _startNewGame());
              Navigator.pop(context);
            },
            child: const Text('Play Again'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.pop();
            },
            child: const Text('Exit'),
          ),
        ],
      ),
    );
  }
}

// ======================== WORD SEARCH ========================
class WordSearchGame extends StatefulWidget {
  const WordSearchGame({super.key});

  @override
  State<WordSearchGame> createState() => _WordSearchGameState();
}

class _WordSearchGameState extends State<WordSearchGame> {
  final List<String> words = ['SCHOOL', 'BOOKS', 'STUDY', 'MATH', 'SCIENCE', 'LEARN'];
  late String currentWord;
  late List<String> scrambled;
  int score = 0;
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _nextWord();
  }

  void _nextWord() {
    currentWord = words[Random().nextInt(words.length)];
    scrambled = currentWord.split('')..shuffle();
  }

  void _check() {
    if (_controller.text.toUpperCase() == currentWord) {
      setState(() {
        score++;
        _nextWord();
        _controller.clear();
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Correct!')));
      _showWinDialog();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Try Again!')));
    }
  }

  void _showWinDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Correct!'),
        content: Text('The word was indeed $currentWord!'),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                _nextWord();
                _controller.clear();
              });
              Navigator.pop(context);
            },
            child: const Text('Next Word'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.pop();
            },
            child: const Text('Exit'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Word Scramble')),
      body: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          children: [
            Text('Score: $score', style: const TextStyle(fontSize: 24)),
            const Spacer(),
            Text(scrambled.join(' '), style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold, letterSpacing: 4)),
            const SizedBox(height: 40),
            TextField(
              controller: _controller,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 32),
              decoration: const InputDecoration(hintText: 'Unscramble it!'),
              onSubmitted: (_) => _check(),
            ),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: _check, child: const Text('Check')),
            const Spacer(flex: 2),
          ],
        ),
      ),
    );
  }
}
