import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/exam.dart';

final examRepositoryProvider = Provider((ref) => ExamRepository(ref));

class ExamRepository {
  final Ref _ref;

  ExamRepository(this._ref);

  Future<List<Exam>> getExams() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/exams/');
      final dynamic data = response.data;
      final List results = (data is Map) ? (data['results'] ?? []) : (data ?? []);
      return results.map((e) => Exam.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<List<ExamResult>> getResults() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/results/');
      final dynamic data = response.data;
      final List results = (data is Map) ? (data['results'] ?? []) : (data ?? []);
      return results.map((e) => ExamResult.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<ExamResult> getResultDetail(String id) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/results/$id/');
      return ExamResult.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }
}

final examsProvider = FutureProvider<List<Exam>>((ref) async {
  return ref.read(examRepositoryProvider).getExams();
});

final examResultsProvider = FutureProvider<List<ExamResult>>((ref) async {
  return ref.read(examRepositoryProvider).getResults();
});

final resultDetailProvider = FutureProvider.family<ExamResult, String>((ref, id) async {
  return ref.read(examRepositoryProvider).getResultDetail(id);
});
