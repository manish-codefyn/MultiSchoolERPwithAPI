// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'message.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Message _$MessageFromJson(Map<String, dynamic> json) => Message(
  id: json['id'] as String,
  senderName: json['sender_name'] as String,
  text: json['text'] as String,
  sentAt: json['sent_at'] as String,
  isMe: json['is_me'] as bool,
);

Map<String, dynamic> _$MessageToJson(Message instance) => <String, dynamic>{
  'id': instance.id,
  'sender_name': instance.senderName,
  'text': instance.text,
  'sent_at': instance.sentAt,
  'is_me': instance.isMe,
};

MessageThread _$MessageThreadFromJson(Map<String, dynamic> json) =>
    MessageThread(
      id: json['id'] as String,
      otherParticipant: json['other_participant'] as String,
      lastMessage: json['last_message'] as String?,
      updatedAt: json['updated_at'] as String,
      unreadCount: (json['unread_count'] as num).toInt(),
    );

Map<String, dynamic> _$MessageThreadToJson(MessageThread instance) =>
    <String, dynamic>{
      'id': instance.id,
      'other_participant': instance.otherParticipant,
      'last_message': instance.lastMessage,
      'updated_at': instance.updatedAt,
      'unread_count': instance.unreadCount,
    };
