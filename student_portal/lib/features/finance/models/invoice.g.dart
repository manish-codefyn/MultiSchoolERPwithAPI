// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invoice.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Invoice _$InvoiceFromJson(Map<String, dynamic> json) => Invoice(
  id: json['id'] as String,
  invoiceNumber: json['invoice_number'] as String,
  issueDate: json['issue_date'] as String,
  dueDate: json['due_date'] as String,
  totalAmount: (json['total_amount'] as num).toDouble(),
  paidAmount: (json['paid_amount'] as num).toDouble(),
  dueAmount: (json['due_amount'] as num).toDouble(),
  status: json['status'] as String,
  statusDisplay: json['status_display'] as String,
  printUrl: json['print_url'] as String?,
  downloadUrl: json['download_url'] as String?,
  items: (json['items'] as List<dynamic>?)
      ?.map((e) => InvoiceItem.fromJson(e as Map<String, dynamic>))
      .toList(),
);

Map<String, dynamic> _$InvoiceToJson(Invoice instance) => <String, dynamic>{
  'id': instance.id,
  'invoice_number': instance.invoiceNumber,
  'issue_date': instance.issueDate,
  'due_date': instance.dueDate,
  'total_amount': instance.totalAmount,
  'paid_amount': instance.paidAmount,
  'due_amount': instance.dueAmount,
  'status': instance.status,
  'status_display': instance.statusDisplay,
  'items': instance.items,
  'print_url': instance.printUrl,
  'download_url': instance.downloadUrl,
};

InvoiceItem _$InvoiceItemFromJson(Map<String, dynamic> json) => InvoiceItem(
  id: json['id'] as String,
  feeTypeName: json['fee_type_name'] as String,
  amount: (json['amount'] as num).toDouble(),
  description: json['description'] as String?,
);

Map<String, dynamic> _$InvoiceItemToJson(InvoiceItem instance) =>
    <String, dynamic>{
      'id': instance.id,
      'fee_type_name': instance.feeTypeName,
      'amount': instance.amount,
      'description': instance.description,
    };
