import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/communications_repository.dart';
import '../models/message.dart';
import '../../../core/theme/app_theme.dart';
import 'package:intl/intl.dart';

class InboxScreen extends ConsumerWidget {
  const InboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final threadsAsync = ref.watch(threadsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Messages')),
      body: threadsAsync.when(
        data: (threads) => threads.isEmpty
            ? const Center(child: Text('No messages yet'))
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: threads.length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final thread = threads[index];
                  return ListTile(
                    contentPadding: const EdgeInsets.symmetric(vertical: 8),
                    leading: CircleAvatar(
                      backgroundColor: AppTheme.primaryBlue.withOpacity(0.1),
                      child: Text(thread.otherParticipant[0]),
                    ),
                    title: Text(thread.otherParticipant, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text(
                      thread.lastMessage ?? 'No messages',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          DateFormat('dd MMM').format(DateTime.parse(thread.updatedAt)),
                          style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                        ),
                        if (thread.unreadCount > 0)
                          Container(
                            margin: const EdgeInsets.only(top: 4),
                            padding: const EdgeInsets.all(6),
                            decoration: const BoxDecoration(color: AppTheme.primaryBlue, shape: BoxShape.circle),
                            child: Text(
                              '${thread.unreadCount}',
                              style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                      ],
                    ),
                    onTap: () => context.push('/messages/${thread.id}'),
                  );
                },
              ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, __) => Center(child: Text('Error: $e')),
      ),
    );
  }
}
