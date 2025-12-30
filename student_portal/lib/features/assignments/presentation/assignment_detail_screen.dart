import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../data/assignments_repository.dart';
import '../models/assignment.dart';
import '../../../core/theme/app_theme.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

class AssignmentDetailScreen extends ConsumerStatefulWidget {
  final String id;
  const AssignmentDetailScreen({super.key, required this.id});

  @override
  ConsumerState<AssignmentDetailScreen> createState() => _AssignmentDetailScreenState();
}

class _AssignmentDetailScreenState extends ConsumerState<AssignmentDetailScreen> {
  final _textController = TextEditingController();
  String? _filePath;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles();
    if (result != null) {
      setState(() {
        _filePath = result.files.single.path;
      });
    }
  }

  void _onSubmit() async {
    setState(() => _isSubmitting = true);
    try {
      await ref.read(assignmentsRepositoryProvider).submitAssignment(
        assignmentId: widget.id,
        text: _textController.text,
        filePath: _filePath,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Assignment submitted successfully!')),
        );
        ref.refresh(assignmentDetailProvider(widget.id));
        ref.refresh(categorizedAssignmentsProvider);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final assignmentAsync = ref.watch(assignmentDetailProvider(widget.id));

    return Scaffold(
      appBar: AppBar(title: const Text('Assignment Detail')),
      body: assignmentAsync.when(
        data: (a) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _StatusBadge(isSubmitted: a.isSubmitted, isOverdue: a.isOverdue, status: a.status),
                      const SizedBox(height: 16),
                      Text(a.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          const Icon(Icons.subject, size: 18, color: AppTheme.textMuted),
                          const SizedBox(width: 8),
                          Text(a.subjectName, style: const TextStyle(color: AppTheme.textMuted)),
                          const Spacer(),
                          const Icon(Icons.star_outline, size: 18, color: AppTheme.textMuted),
                          const SizedBox(width: 4),
                          Text('${a.maxMarks} marks', style: const TextStyle(color: AppTheme.textMuted)),
                        ],
                      ),
                        if (a.attachmentUrl != null) ...[
                        const SizedBox(height: 16),
                        OutlinedButton.icon(
                          onPressed: () async {
                            final url = Uri.parse(a.attachmentUrl!);
                            if (await canLaunchUrl(url)) {
                              await launchUrl(url, mode: LaunchMode.externalApplication);
                            }
                          },
                          icon: const Icon(Icons.download_rounded),
                          label: const Text('Download Attachment'),
                          style: OutlinedButton.styleFrom(
                            minimumSize: const Size.fromHeight(40),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Description
              const Text('Description', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              Text(a.description ?? 'No description provided', style: const TextStyle(height: 1.5)),
              const SizedBox(height: 32),

              // Submission Section
              if (a.isSubmitted)
                _SubmissionInfo(submission: a.submissionStatus!)
              else ...[
                const Text('Submit Your Work', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                TextField(
                  controller: _textController,
                  maxLines: 5,
                  decoration: const InputDecoration(
                    hintText: 'Enter submission text (optional)',
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: _pickFile,
                  icon: const Icon(Icons.attach_file),
                  label: Text(_filePath == null ? 'Attach File' : 'Change File (${_filePath!.split('/').last})'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _isSubmitting ? null : _onSubmit,
                  child: _isSubmitting 
                      ? const CircularProgressIndicator(color: Colors.white) 
                      : const Text('Submit Assignment'),
                ),
              ],
            ],
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, __) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final bool isSubmitted;
  final bool isOverdue;
  final String? status;

  const _StatusBadge({required this.isSubmitted, required this.isOverdue, this.status});

  @override
  Widget build(BuildContext context) {
    Color color = AppTheme.warning;
    String label = 'Pending';

    if (isSubmitted) {
      color = AppTheme.success;
      label = status ?? 'Submitted';
    } else if (isOverdue) {
      color = AppTheme.danger;
      label = 'Overdue';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold),
      ),
    );
  }
}

class _SubmissionInfo extends StatelessWidget {
  final Map<String, dynamic> submission;
  const _SubmissionInfo({required this.submission});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppTheme.success.withOpacity(0.05),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: AppTheme.success.withOpacity(0.2)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.check_circle, color: AppTheme.success, size: 20),
                SizedBox(width: 8),
                Text('Submission Received', style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.success)),
              ],
            ),
            const SizedBox(height: 16),
            Text('Submitted on: ${DateFormat('dd MMM yyyy, hh:mm a').format(DateTime.parse(submission['submitted_at']))}'),
            if (submission['marks_obtained'] != null) ...[
              const SizedBox(height: 12),
              Text('Marks: ${submission['marks_obtained']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            ],
            if (submission['teacher_remarks'] != null) ...[
              const SizedBox(height: 12),
              const Text('Teacher Remarks:', style: TextStyle(fontWeight: FontWeight.bold)),
              Text(submission['teacher_remarks']),
            ],
          ],
        ),
      ),
    );
  }
}
