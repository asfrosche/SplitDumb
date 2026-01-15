import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'core/routing/app_router.dart';
import 'core/theme/app_theme.dart';

void main() {
  runApp(const ProviderScope(child: SplitDumbApp()));
}

class SplitDumbApp extends StatelessWidget {
  const SplitDumbApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'SplitDumb',
      theme: AppTheme.lightTheme,
      routerConfig: AppRouter.router,
    );
  }
}
