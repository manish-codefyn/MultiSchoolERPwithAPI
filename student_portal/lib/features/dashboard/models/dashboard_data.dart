import 'package:json_annotation/json_annotation.dart';
import '../../profile/models/student_profile.dart';
import '../../assignments/models/assignment.dart';

part 'dashboard_data.g.dart';

@JsonSerializable()
class DashboardData {
  final StudentProfile student;
  @JsonKey(name: 'pending_fees')
  final double pendingFees;
  @JsonKey(name: 'pending_invoice_count')
  final int pendingInvoiceCount;
  @JsonKey(name: 'upcoming_assignments')
  final List<Assignment> upcomingAssignments;

  DashboardData({
    required this.student,
    required this.pendingFees,
    required this.pendingInvoiceCount,
    required this.upcomingAssignments,
  });

  factory DashboardData.fromJson(Map<String, dynamic> json) => _$DashboardDataFromJson(json);
  Map<String, dynamic> toJson() => _$DashboardDataToJson(this);
}
