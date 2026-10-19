-- Execute read-only against a backup before applying revision 0006.
-- Every returned row must be investigated; never reassign a tenant by guesswork.
SELECT 'equipment.client' AS relation, e.id AS record_id FROM equipment e JOIN clients c ON c.id=e.cliente_id WHERE e.empresa_id<>c.empresa_id
UNION ALL SELECT 'services.client', s.id FROM services s JOIN clients c ON c.id=s.cliente_id WHERE s.empresa_id<>c.empresa_id
UNION ALL SELECT 'services.equipment', s.id FROM services s JOIN equipment e ON e.id=s.equipo_id WHERE s.empresa_id<>e.empresa_id OR s.cliente_id<>e.cliente_id
UNION ALL SELECT 'services.responsible', s.id FROM services s JOIN users u ON u.id=s.usuario_responsable_id WHERE s.empresa_id IS DISTINCT FROM u.empresa_id
UNION ALL SELECT 'movements.product', m.id FROM inventory_movements m JOIN products p ON p.id=m.producto_id WHERE m.empresa_id<>p.empresa_id
UNION ALL SELECT 'movements.service', m.id FROM inventory_movements m JOIN services s ON s.id=m.servicio_id WHERE m.empresa_id<>s.empresa_id
UNION ALL SELECT 'payments.service', p.id FROM payments p JOIN services s ON s.id=p.servicio_id WHERE p.empresa_id<>s.empresa_id
UNION ALL SELECT 'invoices.service', i.id FROM invoices i JOIN services s ON s.id=i.servicio_id WHERE i.empresa_id<>s.empresa_id OR i.cliente_id<>s.cliente_id
UNION ALL SELECT 'invoices.client', i.id FROM invoices i JOIN clients c ON c.id=i.cliente_id WHERE i.empresa_id<>c.empresa_id
UNION ALL SELECT 'licenses.client', l.id FROM licenses l JOIN clients c ON c.id=l.cliente_id WHERE l.empresa_id<>c.empresa_id
UNION ALL SELECT 'licenses.equipment', l.id FROM licenses l JOIN equipment e ON e.id=l.equipo_id WHERE l.empresa_id<>e.empresa_id OR (l.cliente_id IS NOT NULL AND l.cliente_id<>e.cliente_id)
UNION ALL SELECT 'notifications.client', n.id FROM notifications n JOIN clients c ON c.id=n.cliente_id WHERE n.empresa_id<>c.empresa_id
UNION ALL SELECT 'notifications.service', n.id FROM notifications n JOIN services s ON s.id=n.servicio_id WHERE n.empresa_id<>s.empresa_id OR n.cliente_id<>s.cliente_id
UNION ALL SELECT 'service_items.product', si.id FROM service_items si JOIN services s ON s.id=si.servicio_id JOIN products p ON p.id=si.producto_id WHERE s.empresa_id<>p.empresa_id
UNION ALL SELECT 'invoice_items.product', ii.id FROM invoice_items ii JOIN invoices i ON i.id=ii.comprobante_id JOIN products p ON p.id=ii.producto_id WHERE i.empresa_id<>p.empresa_id
UNION ALL SELECT 'users.role', u.id FROM users u JOIN roles r ON r.id=u.rol_id WHERE (r.nombre='SUPERADMIN' AND u.empresa_id IS NOT NULL) OR (r.nombre<>'SUPERADMIN' AND u.empresa_id IS NULL)
UNION ALL SELECT 'payments.actor', p.id FROM payments p JOIN users u ON u.id=p.usuario_id JOIN roles r ON r.id=u.rol_id WHERE p.empresa_id IS DISTINCT FROM u.empresa_id AND NOT (u.empresa_id IS NULL AND r.nombre='SUPERADMIN')
UNION ALL SELECT 'invoices.actor', i.id FROM invoices i JOIN users u ON u.id=i.usuario_id JOIN roles r ON r.id=u.rol_id WHERE i.empresa_id IS DISTINCT FROM u.empresa_id AND NOT (u.empresa_id IS NULL AND r.nombre='SUPERADMIN')
UNION ALL SELECT 'movements.actor', m.id FROM inventory_movements m JOIN users u ON u.id=m.usuario_id JOIN roles r ON r.id=u.rol_id WHERE m.empresa_id IS DISTINCT FROM u.empresa_id AND NOT (u.empresa_id IS NULL AND r.nombre='SUPERADMIN')
ORDER BY relation, record_id;
