import 'package:json_annotation/json_annotation.dart';

part 'invoice.g.dart';

@JsonSerializable()
class Invoice {
  final String id;
  @JsonKey(name: 'invoice_number')
  final String invoiceNumber;
  @JsonKey(name: 'issue_date')
  final String issueDate;
  @JsonKey(name: 'due_date')
  final String dueDate;
  @JsonKey(name: 'total_amount')
  final double totalAmount;
  @JsonKey(name: 'paid_amount')
  final double paidAmount;
  @JsonKey(name: 'due_amount')
  final double dueAmount;
  final String status;
  @JsonKey(name: 'status_display')
  final String statusDisplay;
  final List<InvoiceItem>? items;

  Invoice({
    required this.id,
    required this.invoiceNumber,
    required this.issueDate,
    required this.dueDate,
    required this.totalAmount,
    required this.paidAmount,
    required this.dueAmount,
    required this.status,
    required this.statusDisplay,
    this.items,
  });

  factory Invoice.fromJson(Map<String, dynamic> json) => _$InvoiceFromJson(json);
  Map<String, dynamic> toJson() => _$InvoiceToJson(this);
}

@JsonSerializable()
class InvoiceItem {
  final String id;
  @JsonKey(name: 'fee_type_name')
  final String feeTypeName;
  final double amount;
  final String? description;

  InvoiceItem({
    required this.id,
    required this.feeTypeName,
    required this.amount,
    this.description,
  });

  factory InvoiceItem.fromJson(Map<String, dynamic> json) => _$InvoiceItemFromJson(json);
  Map<String, dynamic> toJson() => _$InvoiceItemToJson(this);
}
