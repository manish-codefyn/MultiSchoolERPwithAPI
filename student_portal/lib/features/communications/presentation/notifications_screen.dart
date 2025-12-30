import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/communications_repository.dart';
import '../models/notification.dart';
import '../../../core/theme/app_theme.dart';
import 'package:intl/intl.dart';

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notificationsAsync = ref.watch(notificationsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          TextButton(
            onPressed: () {
              // Future: Mark all as read
            },
            child: const Text('Mark all read', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(notificationsProvider.future),
        child: notificationsAsync.when(
          data: (notifications) => notifications.isEmpty
              ? const Center(child: Text('No notifications yet'))
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: notifications.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final n = notifications[index];
                    return _NotificationCard(notification: n);
                  },
                ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, __) => Center(child: Text('Error: $e')),
        ),
      ),
    );
  }
}

class _NotificationCard extends ConsumerWidget {
  final NotificationItem notification;
  const _NotificationCard({required this.notification});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      elevation: notification.isRead ? 0 : 2,
      color: notification.isRead ? Colors.grey[50] : Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: notification.isRead ? BorderSide(color: Colors.grey[200]!) : BorderSide.none,
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: _getIconColor(notification.notificationType).withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            _getIcon(notification.notificationType),
            color: _getIconColor(notification.notificationType),
          ),
        ),
        title: Text(
          notification.title,
          style: TextStyle(
            fontWeight: notification.isRead ? FontWeight.normal : FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(notification.message),
            const SizedBox(height: 8),
            Text(
              DateFormat('dd MMM, hh:mm a').format(DateTime.parse(notification.createdAt)),
              style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
            ),
          ],
        ),
        onTap: () {
          if (!notification.isRead) {
            ref.read(communicationsRepositoryProvider).markNotificationAsRead(notification.id);
            ref.refresh(notificationsProvider);
          }
        },
      ),
    );
  }

  IconData _getIcon(String type) {
    switch (type) {
      case 'ANNOUNCEMENT': return Icons.announcement_rounded;
      case 'ASSIGNMENT': return Icons.assignment_rounded;
      case 'FEE': return Icons.account_balance_wallet_rounded;
      case 'EXAM': return Icons.quiz_rounded;
      default: return Icons.notifications_rounded;
    }
  }

  Color _getIconColor(String type) {
    switch (type) {
      case 'ANNOUNCEMENT': return Colors.blue;
      case 'ASSIGNMENT': return Colors.purple;
      case 'FEE': return Colors.orange;
      case 'EXAM': return Colors.red;
      default: return AppTheme.primaryBlue;
    }
  }
}
