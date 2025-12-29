import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../models/invoice.dart';

final financeRepositoryProvider = Provider((ref) => FinanceRepository(ref));

class FinanceRepository {
  final Ref _ref;

  FinanceRepository(this._ref);

  Future<List<Invoice>> getInvoices() async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/invoices/');
      return (response.data as List).map((e) => Invoice.fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }

  Future<Invoice> getInvoiceDetail(String id) async {
    final dio = _ref.read(apiClientProvider).client;
    try {
      final response = await dio.get('student-portal/invoices/$id/');
      return Invoice.fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }
}

final invoicesProvider = FutureProvider<List<Invoice>>((ref) async {
  return ref.read(financeRepositoryProvider).getInvoices();
});

final invoiceDetailProvider = FutureProvider.family<Invoice, String>((ref, id) async {
  return ref.read(financeRepositoryProvider).getInvoiceDetail(id);
});
