import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/finance_repository.dart';
import '../models/invoice.dart';
import '../../../core/theme/app_theme.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

class InvoiceDetailScreen extends ConsumerWidget {
  final String id;
  const InvoiceDetailScreen({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final invoiceAsync = ref.watch(invoiceDetailProvider(id));

    return Scaffold(
      appBar: AppBar(title: const Text('Invoice Detail')),
      body: invoiceAsync.when(
        data: (inv) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              // Receipt Style Card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Icon(Icons.receipt_long, size: 40, color: AppTheme.primaryBlue),
                          _StatusBadge(status: inv.status, label: inv.statusDisplay),
                        ],
                      ),
                      const SizedBox(height: 24),
                      Text(
                        inv.invoiceNumber,
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Issued on ${DateFormat('dd MMM yyyy').format(DateTime.parse(inv.issueDate))}',
                        style: const TextStyle(color: AppTheme.textMuted),
                      ),
                      const Divider(height: 40),
                      
                      // Items List
                      ...?inv.items?.map((item) => Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(item.feeTypeName, style: const TextStyle(fontWeight: FontWeight.w600)),
                                  if (item.description != null)
                                    Text(item.description!, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                                ],
                              ),
                            ),
                            Text('₹${item.amount}', style: const TextStyle(fontWeight: FontWeight.bold)),
                          ],
                        ),
                      )),
                      
                      const Divider(height: 40),
                      
                      // Totals
                      _TotalRow(label: 'Total Amount', value: '₹${inv.totalAmount}'),
                      const SizedBox(height: 8),
                      _TotalRow(label: 'Paid Amount', value: '₹${inv.paidAmount}', color: AppTheme.success),
                      const Divider(height: 32),
                      _TotalRow(
                        label: 'Balance Due', 
                        value: '₹${inv.dueAmount}', 
                        isBold: true, 
                        color: inv.dueAmount > 0 ? AppTheme.danger : AppTheme.success,
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 32),
              
              if (inv.dueAmount > 0)
                ElevatedButton.icon(
                  onPressed: () {
                    // Integrate Razorpay or other payment gateway
                  },
                  icon: const Icon(Icons.payment),
                  label: const Text('Pay Now'),
                ),
              if (inv.printUrl != null) ...[
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () async {
                    final url = Uri.parse(inv.printUrl!);
                    if (await canLaunchUrl(url)) {
                      await launchUrl(url, mode: LaunchMode.externalApplication);
                    }
                  },
                  icon: const Icon(Icons.print_rounded),
                  label: const Text('Print Preview'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(50),
                  ),
                ),
              ],
              if (inv.downloadUrl != null) ...[
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: () async {
                    final url = Uri.parse(inv.downloadUrl!);
                    if (await canLaunchUrl(url)) {
                      await launchUrl(url, mode: LaunchMode.externalApplication);
                    }
                  },
                  icon: const Icon(Icons.download_rounded),
                  label: const Text('Download PDF'),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size.fromHeight(50),
                    backgroundColor: AppTheme.secondaryBlue,
                    foregroundColor: Colors.white,
                  ),
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

class _TotalRow extends StatelessWidget {
  final String label;
  final String value;
  final bool isBold;
  final Color? color;

  const _TotalRow({
    required this.label, 
    required this.value, 
    this.isBold = false, 
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(
          fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
          fontSize: isBold ? 18 : 14,
        )),
        Text(value, style: TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: isBold ? 18 : 14,
          color: color,
        )),
      ],
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;
  final String label;

  const _StatusBadge({required this.status, required this.label});

  @override
  Widget build(BuildContext context) {
    Color color = AppTheme.info;
    if (status == 'PAID') color = AppTheme.success;
    if (status == 'OVERDUE') color = AppTheme.danger;
    if (status == 'PARTIALLY_PAID') color = AppTheme.warning;

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
