// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'group.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Group _$GroupFromJson(Map<String, dynamic> json) => Group(
      id: json['id'] as int,
      name: json['name'] as String,
      createdByUserId: json['created_by_user_id'] as int,
      defaultCurrency: json['default_currency'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      members: (json['members'] as List<dynamic>)
          .map((e) => GroupMember.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$GroupToJson(Group instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'created_by_user_id': instance.createdByUserId,
      'default_currency': instance.defaultCurrency,
      'created_at': instance.createdAt.toIso8601String(),
      'members': instance.members,
    };

GroupMember _$GroupMemberFromJson(Map<String, dynamic> json) => GroupMember(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      role: json['role'] as String,
      joinedAt: DateTime.parse(json['joined_at'] as String),
      user: User.fromJson(json['user'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$GroupMemberToJson(GroupMember instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'role': instance.role,
      'joined_at': instance.joinedAt.toIso8601String(),
      'user': instance.user,
    };
