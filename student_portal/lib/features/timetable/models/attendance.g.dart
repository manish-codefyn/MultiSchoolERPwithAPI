// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'attendance.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Attendance _$AttendanceFromJson(Map<String, dynamic> json) => Attendance(
  id: json['id'] as String,
  date: json['date'] as String,
  status: json['status'] as String,
  statusDisplay: json['status_display'] as String,
  session: json['session'] as String,
  sessionDisplay: json['session_display'] as String,
  remarks: json['remarks'] as String?,
);

Map<String, dynamic> _$AttendanceToJson(Attendance instance) =>
    <String, dynamic>{
      'id': instance.id,
      'date': instance.date,
      'status': instance.status,
      'status_display': instance.statusDisplay,
      'session': instance.session,
      'session_display': instance.sessionDisplay,
      'remarks': instance.remarks,
    };
