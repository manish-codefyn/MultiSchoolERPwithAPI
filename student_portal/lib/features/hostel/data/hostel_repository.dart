import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/hostel.dart';

final hostelRepositoryProvider = Provider((ref) => HostelRepository(ref));

class HostelRepository {
  final Ref _ref;

  HostelRepository(this._ref);

  Future<HostelDetails> getHostelDetails() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/hostel/details/');
      return HostelDetails.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Hostel>> getHostels() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/hostel/list/');
      final dynamic data = response.data;
      final List results = (data is Map) ? (data['results'] ?? []) : (data ?? []);
      return results.map((e) => Hostel.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }
}

final hostelDetailsProvider = FutureProvider<HostelDetails>((ref) async {
  return ref.read(hostelRepositoryProvider).getHostelDetails();
});

final hostelsProvider = FutureProvider<List<Hostel>>((ref) async {
  return ref.read(hostelRepositoryProvider).getHostels();
});
