// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Assignment _$AssignmentFromJson(Map<String, dynamic> json) => Assignment(
  id: json['id'] as String,
  title: json['title'] as String,
  description: json['description'] as String?,
  assignmentType: json['assignment_type'] as String,
  typeDisplay: json['type_display'] as String,
  subjectName: json['subject_name'] as String,
  className: json['class_name'] as String?,
  assignedDate: json['assigned_date'] as String,
  dueDate: json['due_date'] as String,
  maxMarks: (json['max_marks'] as num).toInt(),
  isOverdue: json['is_overdue'] as bool,
  submissionStatus: json['submission_status'] as Map<String, dynamic>?,
);

Map<String, dynamic> _$AssignmentToJson(Assignment instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'assignment_type': instance.assignmentType,
      'type_display': instance.typeDisplay,
      'subject_name': instance.subjectName,
      'class_name': instance.className,
      'assigned_date': instance.assignedDate,
      'due_date': instance.dueDate,
      'max_marks': instance.maxMarks,
      'is_overdue': instance.isOverdue,
      'submission_status': instance.submissionStatus,
    };
