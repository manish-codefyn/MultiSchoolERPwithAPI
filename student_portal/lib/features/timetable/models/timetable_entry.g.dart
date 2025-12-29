// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'timetable_entry.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TimetableEntry _$TimetableEntryFromJson(Map<String, dynamic> json) =>
    TimetableEntry(
      id: json['id'] as String,
      day: json['day'] as String,
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
      subjectName: json['subject_name'] as String?,
      teacherName: json['teacher_name'] as String?,
      roomName: json['room_name'] as String?,
    );

Map<String, dynamic> _$TimetableEntryToJson(TimetableEntry instance) =>
    <String, dynamic>{
      'id': instance.id,
      'day': instance.day,
      'start_time': instance.startTime,
      'end_time': instance.endTime,
      'subject_name': instance.subjectName,
      'teacher_name': instance.teacherName,
      'room_name': instance.roomName,
    };
