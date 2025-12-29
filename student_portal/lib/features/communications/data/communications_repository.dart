import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/message.dart';

final communicationsRepositoryProvider = Provider((ref) => CommunicationsRepository(ref));

class CommunicationsRepository {
  final Ref _ref;

  CommunicationsRepository(this._ref);

  Future<List<MessageThread>> getThreads() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/inbox/');
      return (response.data as List).map((e) => MessageThread.fromJson(e)).toList();
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
}

final threadsProvider = FutureProvider<List<MessageThread>>((ref) async {
  return ref.read(communicationsRepositoryProvider).getThreads();
});

final threadDetailProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, id) async {
  return ref.read(communicationsRepositoryProvider).getThreadDetail(id);
});
