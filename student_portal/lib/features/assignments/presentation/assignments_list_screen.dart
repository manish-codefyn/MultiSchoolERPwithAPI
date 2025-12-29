import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/assignments_repository.dart';
import '../models/assignment.dart';
import '../../../core/theme/app_theme.dart';
import 'package:intl/intl.dart';

class AssignmentsListScreen extends ConsumerWidget {
  const AssignmentsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final assignmentsAsync = ref.watch(categorizedAssignmentsProvider);

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('My Assignments'),
          bottom: const TabBar(
            indicatorColor: AppTheme.primaryBlue,
            labelColor: AppTheme.primaryBlue,
            unselectedLabelColor: AppTheme.textMuted,
            tabs: [
              Tab(text: 'Pending'),
              Tab(text: 'Overdue'),
              Tab(text: 'Completed'),
            ],
          ),
        ),
        body: assignmentsAsync.when(
          data: (data) {
            final pending = (data['pending'] as List).map((e) => Assignment.fromJson(e)).toList();
            final overdue = (data['overdue'] as List).map((e) => Assignment.fromJson(e)).toList();
            final submitted = (data['submitted'] as List).map((e) => Assignment.fromJson(e)).toList();

            return TabBarView(
              children: [
                _AssignmentList(assignments: pending, emptyMessage: 'No pending assignments'),
                _AssignmentList(assignments: overdue, emptyMessage: 'Great job! Nothing overdue', isOverdue: true),
                _AssignmentList(assignments: submitted, emptyMessage: 'Not submitted any assignments yet', isCompleted: true),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, __) => Center(child: Text('Error: $e')),
        ),
      ),
    );
  }
}

class _AssignmentList extends StatelessWidget {
  final List<Assignment> assignments;
  final String emptyMessage;
  final bool isOverdue;
  final bool isCompleted;

  const _AssignmentList({
    required this.assignments,
    required this.emptyMessage,
    this.isOverdue = false,
    this.isCompleted = false,
  });

  @override
  Widget build(BuildContext context) {
    if (assignments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.assignment_turned_in_outlined, size: 64, color: Colors.grey[300]),
            const SizedBox(height: 16),
            Text(emptyMessage, style: TextStyle(color: Colors.grey[600])),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: assignments.length,
      itemBuilder: (context, index) {
        final a = assignments[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: ListTile(
            contentPadding: const EdgeInsets.all(16),
            title: Text(a.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8),
                Row(
                  children: [
                    _Badge(label: a.subjectName, color: AppTheme.primaryBlue),
                    const SizedBox(width: 8),
                    _Badge(label: a.typeDisplay, color: Colors.grey[600]!),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(Icons.calendar_today, size: 14, color: isOverdue ? AppTheme.danger : AppTheme.textMuted),
                    const SizedBox(width: 4),
                    Text(
                      isCompleted 
                          ? 'Submitted on ${a.submissionStatus?['submitted_at'] != null ? DateFormat('dd MMM').format(DateTime.parse(a.submissionStatus!['submitted_at'])) : "N/A"}'
                          : 'Due ${DateFormat('dd MMM yyyy').format(DateTime.parse(a.dueDate))}',
                      style: TextStyle(
                        fontSize: 12, 
                        color: isOverdue ? AppTheme.danger : AppTheme.textMuted,
                        fontWeight: isOverdue ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            trailing: isCompleted 
                ? const Icon(Icons.check_circle, color: AppTheme.success)
                : const Icon(Icons.chevron_right),
            onTap: () => context.push('/assignments/${a.id}'),
          ),
        );
      },
    );
  }
}

class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  const _Badge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }
}
