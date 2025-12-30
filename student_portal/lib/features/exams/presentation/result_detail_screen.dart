import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../data/exam_repository.dart';
import '../models/exam.dart';

class ResultDetailScreen extends ConsumerWidget {
  final String resultId;

  const ResultDetailScreen({super.key, required this.resultId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final resultAsync = ref.watch(resultDetailProvider(resultId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Result Details'),
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: AppTheme.primaryBlue,
      ),
      body: resultAsync.when(
        data: (result) => _buildDetailView(context, result),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => Center(child: Text('Error: $e')),
      ),
    );
  }

  Widget _buildDetailView(BuildContext context, ExamResult result) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSummaryCard(result),
          const SizedBox(height: 24),
          const Text(
            'Subject Marks',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildMarksTable(result.subjectResults),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(ExamResult result) {
    final statusColor = _getStatusColor(result.resultStatus);
    
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [statusColor, statusColor.withOpacity(0.8)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          children: [
            Text(
              result.examName,
              style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              result.examType,
              style: TextStyle(color: Colors.white.withOpacity(0.9)),
            ),
            const SizedBox(height: 20),
            const Divider(color: Colors.white24),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('Score', '${result.obtainedMarks}/${result.totalMarks}'),
                _buildStatItem('Percentage', '${result.percentage}%'),
                _buildStatItem('Grade', result.overallGradeDisplay),
                _buildStatItem('Status', result.statusDisplay),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildMarksTable(List<SubjectResult> subjects) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            ),
            child: const Row(
              children: [
                Expanded(flex: 3, child: Text('Subject', style: TextStyle(fontWeight: FontWeight.bold))),
                Expanded(child: Text('Marks', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold))),
                Expanded(child: Text('Max', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold))),
                Expanded(child: Text('Grade', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold))),
              ],
            ),
          ),
          ...subjects.map((s) => Column(
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                child: Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: Text(s.subjectName, style: const TextStyle(fontWeight: FontWeight.w500)),
                    ),
                    Expanded(
                      child: Text(
                        s.isAbsent ? 'ABS' : s.totalMarks,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: _isPass(s) ? Colors.black : Colors.red,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                    Expanded(
                      child: Text(s.maxMarks, textAlign: TextAlign.center),
                    ),
                    Expanded(
                      child: Text(s.gradePoint ?? '-', textAlign: TextAlign.center),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
            ],
          )),
        ],
      ),
    );
  }

  bool _isPass(SubjectResult s) {
    if (s.isAbsent) return false;
    try {
      double total = double.parse(s.totalMarks);
      double pass = double.parse(s.passMarks);
      return total >= pass;
    } catch (e) {
      return true;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'PASS':
        return Colors.green;
      case 'FAIL':
        return Colors.red;
      case 'COMPARTMENT':
        return Colors.orange;
      case 'ABSENT':
        return Colors.grey;
      default:
        return AppTheme.primaryBlue;
    }
  }
}
