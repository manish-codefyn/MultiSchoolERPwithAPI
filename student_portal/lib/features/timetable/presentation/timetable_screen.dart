import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/timetable_repository.dart';
import '../models/timetable_entry.dart';
import '../../../core/theme/app_theme.dart';

class TimetableScreen extends ConsumerWidget {
  const TimetableScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timetableAsync = ref.watch(timetableProvider);
    final days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    return DefaultTabController(
      length: days.length,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('My Timetable'),
          bottom: TabBar(
            isScrollable: true,
            indicatorColor: AppTheme.primaryBlue,
            labelColor: AppTheme.primaryBlue,
            unselectedLabelColor: AppTheme.textMuted,
            tabs: days.map((day) => Tab(text: day)).toList(),
          ),
        ),
        body: timetableAsync.when(
          data: (data) => TabBarView(
            children: days.map((day) {
              final entries = data[day] ?? [];
              if (entries.isEmpty) {
                return const Center(child: Text('No classes scheduled for this day'));
              }
              return ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: entries.length,
                itemBuilder: (context, index) {
                  final entry = entries[index];
                  return _TimetableCard(entry: entry);
                },
              );
            }).toList(),
          ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, __) => Center(child: Text('Error: $e')),
        ),
      ),
    );
  }
}

class _TimetableCard extends StatelessWidget {
  final TimetableEntry entry;
  const _TimetableCard({required this.entry});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            // Time Column
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.startTime,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                Text(
                  entry.endTime,
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
                ),
              ],
            ),
            const VerticalDivider(width: 32),
            const SizedBox(width: 8),
            // Subject Column
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    entry.subjectName ?? 'Unknown Subject',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.person_outline, size: 14, color: AppTheme.textMuted),
                      const SizedBox(width: 4),
                      Text(entry.teacherName ?? 'N/A', style: const TextStyle(color: AppTheme.textMuted, fontSize: 13)),
                      if (entry.roomName != null && entry.roomName!.isNotEmpty) ...[
                        const SizedBox(width: 12),
                        const Icon(Icons.room_outlined, size: 14, color: AppTheme.textMuted),
                        const SizedBox(width: 4),
                        Text(entry.roomName!, style: const TextStyle(color: AppTheme.textMuted, fontSize: 13)),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
