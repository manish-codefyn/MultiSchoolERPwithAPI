import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/message.dart';
import '../models/notification.dart';

final communicationsRepositoryProvider = Provider((ref) => CommunicationsRepository(ref));

class CommunicationsRepository {
  final Ref _ref;

  CommunicationsRepository(this._ref);

  Future<List<MessageThread>> getThreads() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/inbox/');
      final dynamic responseData = response.data;
      List results;
      if (responseData is Map && responseData.containsKey('results')) {
        results = responseData['results'] as List;
      } else {
        results = responseData as List;
      }
      return results.map((e) => MessageThread.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getThreadDetail(String id) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/threads/$id/');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> sendMessage(String threadId, String text) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      await dio.post('student-portal/threads/$threadId/send/', data: {'text': text});
    } catch (e) {
      rethrow;
    }
  }

  Future<List<NotificationItem>> getNotifications() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/notifications/');
      final dynamic responseData = response.data;
      List results;
      if (responseData is Map && responseData.containsKey('results')) {
        results = responseData['results'] as List;
      } else {
        results = responseData as List;
      }
      return results.map((e) => NotificationItem.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> markNotificationAsRead(String id) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      await dio.post('student-portal/notifications/$id/read/');
    } catch (e) {
      rethrow;
    }
  }
}

final notificationsProvider = FutureProvider<List<NotificationItem>>((ref) async {
  return ref.read(communicationsRepositoryProvider).getNotifications();
});

final threadsProvider = FutureProvider<List<MessageThread>>((ref) async {
  return ref.read(communicationsRepositoryProvider).getThreads();
});

final threadDetailProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, id) async {
  return ref.read(communicationsRepositoryProvider).getThreadDetail(id);
});
