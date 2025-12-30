import 'package:json_annotation/json_annotation.dart';

part 'attendance.g.dart';

@JsonSerializable()
class Attendance {
  final String id;
  final String date;
  final String status;
  @JsonKey(name: 'status_display')
  final String statusDisplay;
  final String session;
  @JsonKey(name: 'session_display')
  final String sessionDisplay;
  final String? remarks;

  Attendance({
    required this.id,
    required this.date,
    required this.status,
    required this.statusDisplay,
    required this.session,
    required this.sessionDisplay,
    this.remarks,
  });

  factory Attendance.fromJson(Map<String, dynamic> json) => _$AttendanceFromJson(json);
  Map<String, dynamic> toJson() => _$AttendanceToJson(this);
}
