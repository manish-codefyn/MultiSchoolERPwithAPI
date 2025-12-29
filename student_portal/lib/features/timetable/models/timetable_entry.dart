import 'package:json_annotation/json_annotation.dart';

part 'timetable_entry.g.dart';

@JsonSerializable()
class TimetableEntry {
  final String id;
  final String day;
  @JsonKey(name: 'start_time')
  final String startTime;
  @JsonKey(name: 'end_time')
  final String endTime;
  @JsonKey(name: 'subject_name')
  final String? subjectName;
  @JsonKey(name: 'teacher_name')
  final String? teacherName;
  @JsonKey(name: 'room_name')
  final String? roomName;

  TimetableEntry({
    required this.id,
    required this.day,
    required this.startTime,
    required this.endTime,
    this.subjectName,
    this.teacherName,
    this.roomName,
  });

  factory TimetableEntry.fromJson(Map<String, dynamic> json) => _$TimetableEntryFromJson(json);
  Map<String, dynamic> toJson() => _$TimetableEntryToJson(this);
}
