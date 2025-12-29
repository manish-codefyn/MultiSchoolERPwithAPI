// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dashboard_data.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DashboardData _$DashboardDataFromJson(Map<String, dynamic> json) =>
    DashboardData(
      student: StudentProfile.fromJson(json['student'] as Map<String, dynamic>),
      pendingFees: (json['pending_fees'] as num).toDouble(),
      pendingInvoiceCount: (json['pending_invoice_count'] as num).toInt(),
      upcomingAssignments: (json['upcoming_assignments'] as List<dynamic>)
          .map((e) => Assignment.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$DashboardDataToJson(DashboardData instance) =>
    <String, dynamic>{
      'student': instance.student,
      'pending_fees': instance.pendingFees,
      'pending_invoice_count': instance.pendingInvoiceCount,
      'upcoming_assignments': instance.upcomingAssignments,
    };
