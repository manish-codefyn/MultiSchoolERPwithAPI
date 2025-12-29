import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/timetable_entry.dart';

final timetableRepositoryProvider = Provider((ref) => TimetableRepository(ref));

class TimetableRepository {
  final Ref _ref;

  TimetableRepository(this._ref);

  Future<Map<String, List<TimetableEntry>>> getTimetable() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/timetable/');
      final Map<String, dynamic> data = response.data;
      
      return data.map((key, value) => MapEntry(
            key,
            (value as List).map((e) => TimetableEntry.fromJson(e)).toList(),
          ));
    } catch (e) {
      rethrow;
    }
  }
}

final timetableProvider = FutureProvider<Map<String, List<TimetableEntry>>>((ref) async {
  return ref.read(timetableRepositoryProvider).getTimetable();
});
